from pokemondb_net_scrapers.models.move import Move
from pokemondb_net_scrapers.moves_pipeline.html import AllMovesPage
from pokemondb_net_scrapers.utils import parsing


class AllMovesScraper:
    def __init__(self, url: str) -> None:
        self._page = AllMovesPage(url)

    def list_moves(self) -> list[Move]:
        result = []

        for row in self._page.select_move_rows():
            name = row.select_name()
            result.append(Move(
                name,
                parsing.convertToId(name),
                row.select_type(),
                row.select_category(),
                row.select_power(),
                row.select_accuracy(),
                row.select_pp(),
                row.select_effect(),
                row.select_probability(),
            ))

        return result
