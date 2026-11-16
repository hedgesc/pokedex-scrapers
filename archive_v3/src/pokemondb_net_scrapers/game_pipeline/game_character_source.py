from typing import Protocol, runtime_checkable

from pokemondb_net_scrapers.models.game import Game
from pokemondb_net_scrapers.models.game_character import GameCharacter


@runtime_checkable
class GameCharacterSource(Protocol):
    """Where GameCharacterBuilder gets its per-game character rows from.

    Implementations only scrape facts - they don't resolve characterId (that
    requires a cache lookup, which GameCharacterBuilder owns) and don't need
    to set gameId either (GameCharacterBuilder assigns it, since it's the one
    iterating games). Both fields can be left at GameCharacter's defaults.
    """

    def list_game_characters(self, url: str) -> list[GameCharacter]:
        """Scrape the given url and return one GameCharacter row per
        character that appears in it, with nameId/pokemonId/thumbnailUrl set."""
        ...
