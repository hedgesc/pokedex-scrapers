from pokemondb_net_scrapers.characters_pipeline.html import CharacterMovesPage
from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.character_seed import CharacterSeed
from pokemondb_net_scrapers.models.game_character_move import GameCharacterMove


class CharacterMovesScraper:
    def __init__(self, url: str) -> None:
        self._generation = _generation_from_url(url)
        self._page = CharacterMovesPage(url)

    def build_character_moves(self, seed: CharacterSeed) -> list[GameCharacterMove]:
        rows = []

        for dex_name, moves in self._page.select_game_moves():
            for index, move in enumerate(moves):
                row = GameCharacterMove(seed.characterId, dex_name, self._generation, move)

                if index < 4:
                    row.isSuggested = True

                rows.append(row)

        return rows


def _generation_from_url(url: str) -> int:
    tail = url.rstrip("/").split("/")[-1]
    return int(tail) if tail.isdigit() else settings.current_gen
