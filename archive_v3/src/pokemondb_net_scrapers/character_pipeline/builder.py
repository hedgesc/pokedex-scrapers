import logging

from pokemondb_net_scrapers.config import CacheConfig
from pokemondb_net_scrapers.interfaces import CacheClient
from pokemondb_net_scrapers.models.character import Character

from .source import CharacterSource

logger = logging.getLogger(__name__)


class CharacterBuilder:
    """Scrapes the full Character list via a CharacterSource, caches each
    character's nameId -> characterId, and returns the list.

    Numbering and caching live here (not in the source) so a CharacterSource
    implementation stays a stateless scraper: it never needs to know how ids
    are assigned across the whole run.
    """

    def __init__(
        self,
        source: CharacterSource,
        cache_client: CacheClient,
        cache_config: CacheConfig | None = None,
    ) -> None:
        self._source = source
        self._cache = cache_client
        self._cache_cfg = cache_config or CacheConfig()

    def build(self) -> list[Character]:
        characters = self._scrape_all()
        self._cache_characters(characters)
        return characters

    def _scrape_all(self) -> list[Character]:
        characters: list[Character] = []
        next_id = 1

        for seed in self._source.list_seed_characters():
            for variant in self._source.build_character_variants(seed):
                variant.characterId = next_id
                next_id += 1
                characters.append(variant)

        return characters

    def _cache_characters(self, characters: list[Character]) -> None:
        for c in characters:
            key = f"{self._cache_cfg.characters_key_prefix}{c.nameId}"

            try:
                self._cache.set(key, str(c.characterId), ttl=self._cache_cfg.ttl_seconds)
            except Exception:
                logger.exception("Failed to cache character %s (%s)", c.name, c.nameId)

                if self._cache_cfg.raise_on_cache_error:
                    raise
