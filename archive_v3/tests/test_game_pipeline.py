import pytest

from pokemondb_net_scrapers.config import CacheConfig, settings
from pokemondb_net_scrapers.game_pipeline import (
	CacheKeyNotFoundError,
	GameBuilder,
	GameCharacterBuilder,
	GameCharacterSource,
	GameSource,
	PokemonDbGameCharacterSource,
	StaticYamlGameSource,
)
from pokemondb_net_scrapers.models.game import Game
from pokemondb_net_scrapers.models.game_character import GameCharacter
from pokemondb_net_scrapers.static import repo


class FakeGameSource:
    def __init__(self, games):
        self._games = games

    def list_games(self):
        return self._games


def test_fake_game_source_satisfies_game_source_protocol():
    assert isinstance(FakeGameSource([]), GameSource)


def test_static_yaml_game_source_satisfies_game_source_protocol():
    assert isinstance(StaticYamlGameSource(), GameSource)


def test_build_returns_list_of_games_from_source():
    red = Game(1, 1, "Red", "red", ["Kanto"])
    blue = Game(2, 1, "Blue", "blue", ["Kanto"])

    result = GameBuilder(FakeGameSource([red, blue])).build()

    assert result == [red, blue]


def test_build_returns_empty_list_when_source_has_no_games():
    assert GameBuilder(FakeGameSource([])).build() == []


def test_static_yaml_game_source_list_games_delegates_to_static_repo():
    assert StaticYamlGameSource().list_games() == repo.listGames()


def test_game_builder_with_static_yaml_source_includes_known_game():
    games = GameBuilder(StaticYamlGameSource()).build()
    red = next(g for g in games if g.nameId == "red")

    assert red.gameId == 1
    assert red.dexId == 1
    assert red.name == "Red"
    assert red.regions == ["Kanto"]


# --- GameCharacterBuilder --------------------------------------------------
#
# GameCharacterBuilder resolves each Game's dex page URL itself: it looks up
# the Game's dexId in the cache (populated by DexBuilder, under
# CacheConfig.dexes_key_prefix) to get the Dex's nameId, builds the page URL
# from that, and only then asks the source for that page's characters - so
# the source is keyed by url, not by Game, and the cache needs both a
# "dexes:<dexId>" entry and a "characters:<nameId>" entry per row.

class FakeGameCharacterSource:
    def __init__(self, characters_by_url):
        # characters_by_url: {url: [(nameId, pokemonId, thumbnailUrl), ...]}.
        # Stored as plain field tuples rather than live GameCharacter
        # instances so each list_game_characters() call builds fresh objects
        # - matching a real scrape, which re-parses the page every call. Two
        # games sharing a dex both call this with the same url, and the
        # builder mutates each returned GameCharacter in place; reusing the
        # same instances across those calls would let one game's mutation
        # bleed into the other's already-appended result row.
        self._characters_by_url = characters_by_url

    def list_game_characters(self, url):
        return [GameCharacter(*fields) for fields in self._characters_by_url.get(url, [])]


class FakeCacheClient:
    def __init__(self, values):
        self._values = dict(values)

    def set(self, key, value, ttl=None):
        self._values[key] = value

    def get(self, key):
        return self._values.get(key)


def test_fake_game_character_source_satisfies_protocol():
    assert isinstance(FakeGameCharacterSource({}), GameCharacterSource)


def test_pokemondb_game_character_source_satisfies_protocol():
    assert isinstance(PokemonDbGameCharacterSource(), GameCharacterSource)


def test_build_returns_empty_list_when_no_games():
    result = GameCharacterBuilder(FakeGameCharacterSource({}), [], FakeCacheClient({})).build()
    assert result == []


def test_build_sets_game_id_and_resolves_character_id_from_cache():
    red = Game(1, 1, "Red", "red", ["Kanto"])
    dex_url = settings.game_dex_url("red-blue-yellow")
    source = FakeGameCharacterSource({dex_url: [("bulbasaur", "0001", "thumb.png")]})
    cache = FakeCacheClient({"dexes:1": "red-blue-yellow", "characters:bulbasaur": "42"})

    result = GameCharacterBuilder(source, [red], cache).build()

    assert len(result) == 1
    assert result[0].gameId == 1
    assert result[0].characterId == 42


def test_build_iterates_all_given_games_and_reuses_a_shared_dex_lookup():
    red = Game(1, 1, "Red", "red", ["Kanto"])
    blue = Game(2, 1, "Blue", "blue", ["Kanto"])  # shares dexId 1 with red
    gold = Game(4, 2, "Gold", "gold", ["Johto"])

    kanto_url = settings.game_dex_url("red-blue-yellow")
    johto_url = settings.game_dex_url("gold-silver-crystal")

    source = FakeGameCharacterSource({
        kanto_url: [("bulbasaur", "0001", "thumb.png")],
        johto_url: [("chikorita", "0152", "thumb2.png")],
    })
    cache = FakeCacheClient({
        "dexes:1": "red-blue-yellow",
        "dexes:2": "gold-silver-crystal",
        "characters:bulbasaur": "1",
        "characters:chikorita": "152",
    })

    result = GameCharacterBuilder(source, [red, blue, gold], cache).build()

    assert [(gc.gameId, gc.characterId, gc.nameId) for gc in result] == [
        (1, 1, "bulbasaur"),
        (2, 1, "bulbasaur"),
        (4, 152, "chikorita"),
    ]


def test_build_uses_configured_cache_key_prefixes():
    red = Game(1, 1, "Red", "red", ["Kanto"])
    dex_url = settings.game_dex_url("red-blue-yellow")
    source = FakeGameCharacterSource({dex_url: [("bulbasaur", "0001", "thumb.png")]})
    cache = FakeCacheClient({"d:1": "red-blue-yellow", "c:bulbasaur": "7"})

    result = GameCharacterBuilder(
        source, [red], cache, CacheConfig(characters_key_prefix="c:", dexes_key_prefix="d:")
    ).build()

    assert result[0].characterId == 7


def test_build_raises_when_character_name_id_not_cached():
    red = Game(1, 1, "Red", "red", ["Kanto"])
    dex_url = settings.game_dex_url("red-blue-yellow")
    source = FakeGameCharacterSource({dex_url: [("missingno", "000", "thumb.png")]})
    cache = FakeCacheClient({"dexes:1": "red-blue-yellow"})

    with pytest.raises(CacheKeyNotFoundError):
        GameCharacterBuilder(source, [red], cache).build()


def test_build_raises_when_dex_name_id_not_cached():
    red = Game(1, 1, "Red", "red", ["Kanto"])
    source = FakeGameCharacterSource({})
    cache = FakeCacheClient({})

    with pytest.raises(CacheKeyNotFoundError):
        GameCharacterBuilder(source, [red], cache).build()
