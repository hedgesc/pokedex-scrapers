from typing import Protocol, runtime_checkable

from pokemondb_net_scrapers.models.move import Move


@runtime_checkable
class MoveSource(Protocol):
    """Where MoveBuilder gets its data from. Mirrors GameSource/DexSource:
    pokemondb.net's all-moves table fully describes every move on one page,
    so there's no seed/enrich split - a single call returns fully-populated
    Moves (moveId is left at its default; MoveBuilder assigns that).
    """

    def list_moves(self) -> list[Move]:
        """Return every known Move, scraped from the all-moves page."""
        ...
