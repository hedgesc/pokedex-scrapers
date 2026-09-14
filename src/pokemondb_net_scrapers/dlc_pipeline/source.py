from typing import Protocol, runtime_checkable

from pokemondb_net_scrapers.models.dlc import Dlc


@runtime_checkable
class DlcSource(Protocol):
    """Where DlcBuilder gets its data from. Mirrors GameSource/DexSource:
    like games and dexes, dlcs are fully described by hand-maintained YAML
    today, so there's no seed/enrich split - a single call returns
    fully-populated Dlcs.
    """

    def list_dlcs(self) -> list[Dlc]:
        """Return every known Dlc, fully populated."""
        ...
