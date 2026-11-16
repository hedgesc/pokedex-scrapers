import logging

from pokemondb_net_scrapers.config import CacheConfig
from pokemondb_net_scrapers.interfaces import CacheClient
from pokemondb_net_scrapers.models.dex import Dex

from .source import DexSource

logger = logging.getLogger(__name__)


class DexBuilder:
    """Builds the full Dex list via a DexSource and caches each dex's
    dexId -> nameId (under CacheConfig.dexes_key_prefix). Other pipelines -
    e.g. GameCharacterBuilder, to turn a Game's dexId into a dex page URL -
    resolve a dex's nameId through that cache rather than needing the Dex
    list itself.

    Like GameBuilder, there's no per-item scraping/enrichment or id
    assignment to do here (dexId already comes from the YAML) - this only
    adds the caching step on top of the source. Cache-write failures follow
    CharacterBuilder's precedent: logged and skipped by default, or raised
    if CacheConfig.raise_on_cache_error is set.
    """

    def __init__(
        self,
        source: DexSource,
        cache_client: CacheClient,
        cache_config: CacheConfig | None = None,
    ) -> None:
        self._source = source
        self._cache = cache_client
        self._cache_cfg = cache_config or CacheConfig()

    def build(self) -> list[Dex]:
        dexes = self._source.list_dexes()
        self._cache_dexes(dexes)
        return dexes

    def _cache_dexes(self, dexes: list[Dex]) -> None:
        for d in dexes:
            key = f"{self._cache_cfg.dexes_key_prefix}{d.dexId}"

            try:
                self._cache.set(key, d.nameId, ttl=self._cache_cfg.ttl_seconds)
            except Exception:
                logger.exception("Failed to cache dex %s (%s)", d.name, d.dexId)

                if self._cache_cfg.raise_on_cache_error:
                    raise
