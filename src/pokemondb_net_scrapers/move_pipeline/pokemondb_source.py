from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.move import Move
from pokemondb_net_scrapers.utils import parsing

from ._pokemondb_html import AllMovesPage


class PokemonDbMoveSource:
    """MoveSource backed by pokemondb.net's all-moves listing page. All
    markup/selector knowledge lives in _pokemondb_html.py - this class only
    orchestrates it into Moves.
    """

    def __init__(self, all_moves_url: str | None = None) -> None:
        self._all_moves_url = all_moves_url or settings.all_moves_url

    def list_moves(self) -> list[Move]:
        page = AllMovesPage(self._all_moves_url)
        result = []

        for row in page.select_move_rows():
            name = row.select_name()
            move = Move(
                name,
                parsing.convertToId(name),
                row.select_type(),
                row.select_category(),
                row.select_power(),
                row.select_accuracy(),
                row.select_pp(),
                row.select_effect(),
                row.select_probability(),
            )
            result.append(move)

        return result
