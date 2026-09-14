from typing import Protocol, runtime_checkable

from pokemondb_net_scrapers.models.dlc_character import DlcCharacter


@runtime_checkable
class DlcCharacterSource(Protocol):
    """Where DlcCharacterBuilder gets its per-dlc character rows from.

    Implementations only scrape facts - they don't resolve characterId (that
    requires a cache lookup, which DlcCharacterBuilder owns) and don't need
    to set dlcId either (DlcCharacterBuilder assigns it, since it's the one
    iterating dlcs). Both fields can be left at DlcCharacter's defaults.
    """

    def list_dlc_characters(self, url: str) -> list[DlcCharacter]:
        """Scrape the given url and return one DlcCharacter row per
        character that appears in it, with nameId/pokemonId/thumbnailImage set."""
        ...
