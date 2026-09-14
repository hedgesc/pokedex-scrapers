from pokemondb_net_scrapers.character_pipeline.builder import CharacterBuilder
from pokemondb_net_scrapers.config import CacheConfig
from pokemondb_net_scrapers.interfaces import CacheClient
from pokemondb_net_scrapers.models.character import Character
from pokemondb_net_scrapers.testing import InMemoryCacheClient


class FakeClock:
    def __init__(self, start=0.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def test_in_memory_cache_client_satisfies_cache_client_protocol():
    assert isinstance(InMemoryCacheClient(), CacheClient)


def test_get_returns_none_for_missing_key():
    cache = InMemoryCacheClient()
    assert cache.get("characters:bulbasaur") is None


def test_set_then_get_returns_value():
    cache = InMemoryCacheClient()
    cache.set("characters:bulbasaur", "1")
    assert cache.get("characters:bulbasaur") == "1"


def test_set_overwrites_previous_value():
    cache = InMemoryCacheClient()
    cache.set("characters:bulbasaur", "1")
    cache.set("characters:bulbasaur", "2")
    assert cache.get("characters:bulbasaur") == "2"


def test_entry_without_ttl_never_expires():
    clock = FakeClock()
    cache = InMemoryCacheClient(clock=clock)
    cache.set("characters:bulbasaur", "1")

    clock.advance(10_000)

    assert cache.get("characters:bulbasaur") == "1"


def test_entry_expires_after_ttl_elapses():
    clock = FakeClock()
    cache = InMemoryCacheClient(clock=clock)
    cache.set("characters:bulbasaur", "1", ttl=60)

    clock.advance(59)
    assert cache.get("characters:bulbasaur") == "1"

    clock.advance(1)
    assert cache.get("characters:bulbasaur") is None


def test_clear_removes_all_entries():
    cache = InMemoryCacheClient()
    cache.set("characters:bulbasaur", "1")
    cache.set("characters:ivysaur", "2")

    cache.clear()

    assert cache.get("characters:bulbasaur") is None
    assert len(cache) == 0


def test_contains_and_len_reflect_live_entries_only():
    clock = FakeClock()
    cache = InMemoryCacheClient(clock=clock)
    cache.set("characters:bulbasaur", "1")
    cache.set("characters:ivysaur", "2", ttl=10)

    assert "characters:bulbasaur" in cache
    assert "characters:ivysaur" in cache
    assert len(cache) == 2

    clock.advance(11)

    assert "characters:ivysaur" not in cache
    assert len(cache) == 1
    assert cache.keys() == ["characters:bulbasaur"]


# --- Integration with CharacterBuilder -----------------------------------

class FakeCharacterSource:
    def __init__(self, seeds, variants_by_name_id):
        self._seeds = seeds
        self._variants_by_name_id = variants_by_name_id

    def list_seed_characters(self):
        return self._seeds

    def build_character_variants(self, seed):
        return self._variants_by_name_id[seed.nameId]


def test_character_builder_populates_in_memory_cache_client():
    seed = Character("Bulbasaur")
    source = FakeCharacterSource(
        seeds=[seed],
        variants_by_name_id={"bulbasaur": [Character("Bulbasaur")]},
    )
    cache = InMemoryCacheClient()

    result = CharacterBuilder(source, cache, CacheConfig(characters_key_prefix="characters:")).build()

    assert cache.get(f"characters:{result[0].nameId}") == str(result[0].characterId)
