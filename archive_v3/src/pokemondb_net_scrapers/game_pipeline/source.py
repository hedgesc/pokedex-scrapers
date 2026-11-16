from typing import Protocol, runtime_checkable

from pokemondb_net_scrapers.models.game import Game


@runtime_checkable
class GameSource(Protocol):
    """Where GameBuilder gets its data from. Implement this once per data
    source; GameBuilder itself doesn't care where games come from.

    Unlike CharacterSource, there's no seed/enrich split - a Game's fields
    all come from one place (today, the hand-maintained games.yaml), so a
    single call returns fully-populated Games.
    """

    def list_games(self) -> list[Game]:
        """Return every known Game, fully populated."""
        ...
