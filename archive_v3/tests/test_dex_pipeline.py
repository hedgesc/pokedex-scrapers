import pytest

from pokemondb_net_scrapers.config import CacheConfig
from pokemondb_net_scrapers.dex_pipeline import DexBuilder, DexSource, StaticYamlDexSource
from pokemondb_net_scrapers.models.dex import Dex
from pokemondb_net_scrapers.static import repo


class FakeDexSource:
    def __init__(self, dexes):
        self._dexes = dexes

    def list_dexes(self):
        return self._dexes


class RecordingCacheClient:
    def __init__(self, fail_for=frozenset()):
        self.calls = []
        self._fail_for = fail_for

    def set(self, key, value, ttl=None):
        if key in self._fail_for:
            raise RuntimeError("cache unavailable")

        self.calls.append((key, value, ttl))

    def get(self, key):
        for k, v, _ in self.calls:
            if k == key:
                return v

        return None


def test_fake_dex_source_satisfies_dex_source_protocol():
    assert isinstance(FakeDexSource([]), DexSource)


def test_static_yaml_dex_source_satisfies_dex_source_protocol():
    assert isinstance(StaticYamlDexSource(), DexSource)


def test_static_yaml_dex_source_list_dexes_delegates_to_static_repo():
    assert StaticYamlDexSource().list_dexes() == repo.listDexes()


# --- DexBuilder --------------------------------------------------------

def test_build_returns_list_of_dexes_from_source():
    kanto = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)

    result = DexBuilder(FakeDexSource([kanto]), RecordingCacheClient()).build()

    assert result == [kanto]


def test_build_returns_empty_list_when_source_has_no_dexes():
    result = DexBuilder(FakeDexSource([]), RecordingCacheClient()).build()
    assert result == []


def test_build_caches_dex_id_to_name_id_with_default_prefix():
    kanto = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
    cache = RecordingCacheClient()

    DexBuilder(FakeDexSource([kanto]), cache).build()

    assert cache.calls == [("dexes:1", "red-blue-yellow", None)]


def test_build_caches_every_dex():
    kanto = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
    johto = Dex(2, "gold-silver-crystal", "Gold/Silver/Crystal", "Gold, Silver & Crystal", 2)
    cache = RecordingCacheClient()

    DexBuilder(FakeDexSource([kanto, johto]), cache).build()

    assert cache.calls == [
        ("dexes:1", "red-blue-yellow", None),
        ("dexes:2", "gold-silver-crystal", None),
    ]


def test_build_uses_configured_cache_key_prefix():
    kanto = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
    cache = RecordingCacheClient()

    DexBuilder(FakeDexSource([kanto]), cache, CacheConfig(dexes_key_prefix="d:")).build()

    assert cache.calls == [("d:1", "red-blue-yellow", None)]


def test_build_passes_ttl_from_cache_config():
    kanto = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
    cache = RecordingCacheClient()

    DexBuilder(FakeDexSource([kanto]), cache, CacheConfig(ttl_seconds=3600)).build()

    assert cache.calls[0][2] == 3600


def test_build_swallows_cache_errors_by_default():
    kanto = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
    cache = RecordingCacheClient(fail_for={"dexes:1"})

    result = DexBuilder(FakeDexSource([kanto]), cache).build()

    assert result == [kanto]


def test_build_raises_on_cache_error_when_configured():
    kanto = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
    cache = RecordingCacheClient(fail_for={"dexes:1"})

    with pytest.raises(RuntimeError):
        DexBuilder(FakeDexSource([kanto]), cache, CacheConfig(raise_on_cache_error=True)).build()


def test_dex_builder_with_static_yaml_source_includes_known_dex():
    cache = RecordingCacheClient()
    dexes = DexBuilder(StaticYamlDexSource(), cache).build()
    kanto = next(d for d in dexes if d.nameId == "red-blue-yellow")

    assert kanto.dexId == 1
    assert kanto.gen == 1
    assert ("dexes:1", "red-blue-yellow", None) in cache.calls
