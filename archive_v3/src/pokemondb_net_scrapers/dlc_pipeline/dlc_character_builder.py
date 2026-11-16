from pokemondb_net_scrapers.config import CacheConfig, settings
from pokemondb_net_scrapers.interfaces import CacheClient
from pokemondb_net_scrapers.models.dlc import Dlc
from pokemondb_net_scrapers.models.dlc_character import DlcCharacter

from .dlc_character_source import DlcCharacterSource


class CacheKeyNotFoundError(LookupError):
    """Raised when a scraped DlcCharacter's nameId has no cached
    characterId - the character cache is missing or out of date relative
    to what this source just scraped."""

    def __init__(self, key: str, cache_key: str) -> None:
        self.key = key
        self.cache_key = cache_key
        super().__init__(f"No cached entry found for key '{key}' (cache key '{cache_key}')")


class DlcCharacterBuilder:
    """Builds the full DlcCharacter join list: for every given Dlc, scrapes
    which characters appear in it via a DlcCharacterSource, then resolves
    each row's characterId with a cache lookup on nameId (the same
    nameId -> characterId cache CharacterBuilder populates).

    Takes dlcs as a plain list rather than a DlcSource - it has no opinion
    on where the dlcs came from, only that it has them. Mirrors
    GameCharacterBuilder: each Dlc already carries its own nameId, so unlike
    the dex nameId (looked up via the dexId -> nameId cache DexBuilder
    populates) there's no need for a second cache to resolve the dlc's own
    nameId.
    """

    def __init__(
        self,
        source: DlcCharacterSource,
        dlcs: list[Dlc],
        cache_client: CacheClient,
        cache_config: CacheConfig | None = None,
    ) -> None:
        self._source = source
        self._dlcs = dlcs
        self._cache = cache_client
        self._cache_cfg = cache_config or CacheConfig()

    def build(self) -> list[DlcCharacter]:
        result: list[DlcCharacter] = []

        for dlc in self._dlcs:
            dexNameId = self._lookup_dex_name_id(dlc.dexId)
            dlcPageUrl = settings.dlc_dex_url(dexNameId, dlc.nameId)
            for dlc_character in self._source.list_dlc_characters(dlcPageUrl):
                dlc_character.dlcId = dlc.dlcId
                dlc_character.characterId = self._lookup_character_id(dlc_character.nameId)
                result.append(dlc_character)

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
