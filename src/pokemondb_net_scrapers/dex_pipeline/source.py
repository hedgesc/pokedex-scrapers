from typing import Protocol, runtime_checkable

from pokemondb_net_scrapers.models.dex import Dex


@runtime_checkable
class DexSource(Protocol):
    """Where DexBuilder gets its data from. Mirrors GameSource: like games,
    dexes are fully described by hand-maintained YAML today, so there's no
    seed/enrich split - a single call returns fully-populated Dexes.
    """

    def list_dexes(self) -> list[Dex]:
        """Return every known Dex, fully populated."""
        ...
