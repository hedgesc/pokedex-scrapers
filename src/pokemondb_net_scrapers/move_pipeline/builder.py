import logging

from pokemondb_net_scrapers.config import CacheConfig
from pokemondb_net_scrapers.interfaces import CacheClient
from pokemondb_net_scrapers.models.move import Move

from .source import MoveSource

logger = logging.getLogger(__name__)


class MoveBuilder:
    """Scrapes the full Move list via a MoveSource, assigns sequential
    moveIds, caches each move's nameId -> moveId, and returns the list.

    Mirrors CharacterBuilder: numbering and caching live here (not in the
    source) so a MoveSource implementation stays a stateless scraper that
    never needs to know how ids are assigned across the whole run.
    """

    def __init__(
        self,
        source: MoveSource,
        cache_client: CacheClient,
        cache_config: CacheConfig | None = None,
    ) -> None:
        self._source = source
        self._cache = cache_client
        self._cache_cfg = cache_config or CacheConfig()

    def build(self) -> list[Move]:
        moves = self._assign_ids(self._source.list_moves())
        self._cache_moves(moves)
        return moves

    def _assign_ids(self, moves: list[Move]) -> list[Move]:
        for next_id, move in enumerate(moves, start=1):
            move.moveId = next_id

        return moves

    def _cache_moves(self, moves: list[Move]) -> None:
        for m in moves:
            key = f"{self._cache_cfg.moves_key_prefix}{m.nameId}"

            try:
                self._cache.set(key, str(m.moveId), ttl=self._cache_cfg.ttl_seconds)
            except Exception:
                logger.exception("Failed to cache move %s (%s)", m.name, m.nameId)

                if self._cache_cfg.raise_on_cache_error:
                    raise
