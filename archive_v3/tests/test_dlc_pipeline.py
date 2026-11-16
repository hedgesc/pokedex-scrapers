import pytest

from pokemondb_net_scrapers.config import CacheConfig, settings
from pokemondb_net_scrapers.dlc_pipeline import (
	CacheKeyNotFoundError,
	DlcBuilder,
	DlcCharacterBuilder,
	DlcCharacterSource,
	DlcSource,
	PokemonDbDlcCharacterSource,
	StaticYamlDlcSource,
)
from pokemondb_net_scrapers.models.dlc import Dlc
from pokemondb_net_scrapers.models.dlc_character import DlcCharacter
from pokemondb_net_scrapers.static import repo


class FakeDlcSource:
	def __init__(self, dlcs):
		self._dlcs = dlcs

	def list_dlcs(self):
		return self._dlcs


def test_fake_dlc_source_satisfies_dlc_source_protocol():
	assert isinstance(FakeDlcSource([]), DlcSource)


def test_static_yaml_dlc_source_satisfies_dlc_source_protocol():
	assert isinstance(StaticYamlDlcSource(), DlcSource)


def test_build_returns_list_of_dlcs_from_source():
	isle_of_armor = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	crown_tundra = Dlc(2, 15, "The Crown Tundra", "crown-tundra")

	result = DlcBuilder(FakeDlcSource([isle_of_armor, crown_tundra])).build()

	assert result == [isle_of_armor, crown_tundra]


def test_build_returns_empty_list_when_source_has_no_dlcs():
	assert DlcBuilder(FakeDlcSource([])).build() == []


def test_static_yaml_dlc_source_list_dlcs_delegates_to_static_repo():
	assert StaticYamlDlcSource().list_dlcs() == repo.listDlcs()


def test_dlc_builder_with_static_yaml_source_includes_known_dlc():
	dlcs = DlcBuilder(StaticYamlDlcSource()).build()
	isle_of_armor = next(d for d in dlcs if d.nameId == "isle-of-armor")

	assert isle_of_armor.dlcId == 1
	assert isle_of_armor.dexId == 15
	assert isle_of_armor.name == "The Isle of Armor"


# --- DlcCharacterBuilder -----------------------------------------------
#
# DlcCharacterBuilder resolves each Dlc's page URL itself: it looks up the
# Dlc's dexId in the cache (populated by DexBuilder, under
# CacheConfig.dexes_key_prefix) to get the Dex's nameId, builds the page URL
# from that plus the Dlc's own nameId, and only then asks the source for
# that page's characters - so the source is keyed by url, not by Dlc, and
# the cache needs both a "dexes:<dexId>" entry and a "characters:<nameId>"
# entry per row.

class FakeDlcCharacterSource:
	def __init__(self, characters_by_url):
		# characters_by_url: {url: [(nameId, pokemonId, thumbnailImage), ...]}.
		# Stored as plain field tuples rather than live DlcCharacter instances
		# so each list_dlc_characters() call builds fresh objects - matching
		# a real scrape, which re-parses the page every call. Two dlcs
		# sharing a dex both call this with the same url, and the builder
		# mutates each returned DlcCharacter in place; reusing the same
		# instances across those calls would let one dlc's mutation bleed
		# into the other's already-appended result row.
		self._characters_by_url = characters_by_url

	def list_dlc_characters(self, url):
		return [DlcCharacter(*fields) for fields in self._characters_by_url.get(url, [])]


class FakeCacheClient:
	def __init__(self, values):
		self._values = dict(values)

	def set(self, key, value, ttl=None):
		self._values[key] = value

	def get(self, key):
		return self._values.get(key)


def test_fake_dlc_character_source_satisfies_protocol():
	assert isinstance(FakeDlcCharacterSource({}), DlcCharacterSource)


def test_pokemondb_dlc_character_source_satisfies_protocol():
	assert isinstance(PokemonDbDlcCharacterSource(), DlcCharacterSource)


def test_build_returns_empty_list_when_no_dlcs():
	result = DlcCharacterBuilder(FakeDlcCharacterSource({}), [], FakeCacheClient({})).build()
	assert result == []


def test_build_sets_dlc_id_and_resolves_character_id_from_cache():
	isle_of_armor = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	dlc_url = settings.dlc_dex_url("sword-shield", "isle-of-armor")
	source = FakeDlcCharacterSource({dlc_url: [("kubfu", "0891", "thumb.png")]})
	cache = FakeCacheClient({"dexes:15": "sword-shield", "characters:kubfu": "42"})

	result = DlcCharacterBuilder(source, [isle_of_armor], cache).build()

	assert len(result) == 1
	assert result[0].dlcId == 1
	assert result[0].characterId == 42


def test_build_iterates_all_given_dlcs_and_reuses_a_shared_dex_lookup():
	isle_of_armor = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	crown_tundra = Dlc(2, 15, "The Crown Tundra", "crown-tundra")  # shares dexId 15

	isle_url = settings.dlc_dex_url("sword-shield", "isle-of-armor")
	crown_url = settings.dlc_dex_url("sword-shield", "crown-tundra")

	source = FakeDlcCharacterSource({
		isle_url: [("kubfu", "0891", "thumb.png")],
		crown_url: [("regieleki", "0894", "thumb2.png")],
	})
	cache = FakeCacheClient({
		"dexes:15": "sword-shield",
		"characters:kubfu": "891",
		"characters:regieleki": "894",
	})

	result = DlcCharacterBuilder(source, [isle_of_armor, crown_tundra], cache).build()

	assert [(dc.dlcId, dc.characterId, dc.nameId) for dc in result] == [
		(1, 891, "kubfu"),
		(2, 894, "regieleki"),
	]


def test_build_uses_configured_cache_key_prefixes():
	isle_of_armor = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	dlc_url = settings.dlc_dex_url("sword-shield", "isle-of-armor")
	source = FakeDlcCharacterSource({dlc_url: [("kubfu", "0891", "thumb.png")]})
	cache = FakeCacheClient({"d:15": "sword-shield", "c:kubfu": "7"})

	result = DlcCharacterBuilder(
		source, [isle_of_armor], cache, CacheConfig(characters_key_prefix="c:", dexes_key_prefix="d:")
	).build()

	assert result[0].characterId == 7


def test_build_raises_when_character_name_id_not_cached():
	isle_of_armor = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	dlc_url = settings.dlc_dex_url("sword-shield", "isle-of-armor")
	source = FakeDlcCharacterSource({dlc_url: [("missingno", "000", "thumb.png")]})
	cache = FakeCacheClient({"dexes:15": "sword-shield"})

	with pytest.raises(CacheKeyNotFoundError):
		DlcCharacterBuilder(source, [isle_of_armor], cache).build()


def test_build_raises_when_dex_name_id_not_cached():
	isle_of_armor = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	source = FakeDlcCharacterSource({})
	cache = FakeCacheClient({})

	with pytest.raises(CacheKeyNotFoundError):
		DlcCharacterBuilder(source, [isle_of_armor], cache).build()
