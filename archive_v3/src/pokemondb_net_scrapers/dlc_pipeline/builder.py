from pokemondb_net_scrapers.models.dlc import Dlc

from .source import DlcSource


class DlcBuilder:
    """Builds the full Dlc list via a DlcSource.

    Deliberately thin compared to CharacterBuilder/DexBuilder: dlcs aren't
    scraped per-item, and DlcCharacterBuilder gets the Dlc list (with its own
    nameId already on each row) directly rather than through a cache, so
    there's no numbering/enrichment/cache step to own here - this just
    delegates to the source. It exists mainly so callers get the same
    Builder-shaped entry point (`.build() -> list[X]`) across pipelines, like
    GameBuilder.
    """

    def __init__(self, source: DlcSource) -> None:
        self._source = source

    def build(self) -> list[Dlc]:
        return self._source.list_dlcs()
