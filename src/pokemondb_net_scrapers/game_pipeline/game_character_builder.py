from pokemondb_net_scrapers.config import CacheConfig, settings
from pokemondb_net_scrapers.interfaces import CacheClient
from pokemondb_net_scrapers.models.game import Game
from pokemondb_net_scrapers.models.game_character import GameCharacter

from .game_character_source import GameCharacterSource


class CacheKeyNotFoundError(LookupError):
    """Raised when a scraped GameCharacter's nameId has no cached
    characterId - the character cache is missing or out of date relative
    to what this source just scraped."""

    def __init__(self, key: str, cache_key: str) -> None:
        self.key = key
        self.cache_key = cache_key
        super().__init__(f"No cached entry found for key '{key}' (cache key '{cache_key}')")


class GameCharacterBuilder:
    """Builds the full GameCharacter join list: for every given Game, scrapes
    which characters appear in it via a GameCharacterSource, then resolves
    each row's characterId with a cache lookup on nameId (the same
    nameId -> characterId cache CharacterBuilder populates).

    Takes games as a plain list rather than a GameSource - it has no opinion
    on where the games came from, only that it has them.
    """

    def __init__(
        self,
        source: GameCharacterSource,
        games: list[Game],
        cache_client: CacheClient,
        cache_config: CacheConfig | None = None,
    ) -> None:
        self._source = source
        self._games = games
        self._cache = cache_client
        self._cache_cfg = cache_config or CacheConfig()

    def build(self) -> list[GameCharacter]:
        result: list[GameCharacter] = []

        for game in self._games:
            dexNameId = self._lookup_dex_name_id(game.dexId)
            dexPageUrl = settings.game_dex_url(dexNameId)
            for game_character in self._source.list_game_characters(dexPageUrl):
                game_character.gameId = game.gameId
                game_character.characterId = self._lookup_character_id(game_character.nameId)
                result.append(game_character)

        return result

    def _lookup_character_id(self, nameId: str) -> int:
        cache_key = f"{self._cache_cfg.characters_key_prefix}{nameId}"
        cached = self._cache.get(cache_key)

        if cached is None:
            raise CacheKeyNotFoundError(nameId, cache_key)

        return int(cached)

    def _lookup_dex_name_id(self, dexId: int) -> str:
        cache_key = f"{self._cache_cfg.dexes_key_prefix}{str(dexId)}"
        cached = self._cache.get(cache_key)

        if cached is None:
            raise CacheKeyNotFoundError(str(dexId), cache_key)

        return cached
