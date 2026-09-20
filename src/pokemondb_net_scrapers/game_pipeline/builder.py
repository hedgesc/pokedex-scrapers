from pokemondb_net_scrapers.models.game import Game

from .source import GameSource


class GameBuilder:
    """Builds the full Game list via a GameSource.

    Deliberately thin compared to CharacterBuilder: games aren't scraped
    per-item and don't need caching, so there's no numbering/enrichment/cache
    step to own here - this just delegates to the source. It exists mainly so
    callers get the same Builder-shaped entry point (`.build() -> list[X]`)
    across pipelines.
    """

    def __init__(self, source: GameSource) -> None:
        self._source = source

    def build(self) -> list[Game]:
        return self._source.list_games()
