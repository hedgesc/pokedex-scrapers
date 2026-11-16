"""Private HTML-selector knowledge for PokemonDbMoveSource.

Every BeautifulSoup selector pokemondb.net's markup requires lives here, and
only here. If the page's markup changes, this is the only module that should
need to change - pokemondb_source.py just orchestrates this wrapper class.
"""

from bs4 import Tag

from pokemondb_net_scrapers.utils import web


class MoveRowTag:
    def __init__(self, tag: Tag) -> None:
        self._cols = tag.find_all("td")

    def select_name(self) -> str:
        return self._cols[0].select_one("a").get_text()

    def select_type(self) -> str:
        anchor = self._cols[1].select_one("a")
        return "" if anchor is None else anchor.get_text()

    def select_category(self) -> str:
        img = self._cols[2].select_one("img")
        return "" if img is None else img.attrs["title"]

    def select_power(self) -> str:
        return self._cols[3].get_text()

    def select_accuracy(self) -> str:
        return self._cols[4].get_text()

    def select_pp(self) -> str:
        return self._cols[5].get_text()

    def select_effect(self) -> str:
        return self._cols[7].get_text()

    def select_probability(self) -> str:
        return self._cols[8].get_text()


class AllMovesPage:
    def __init__(self, url: str) -> None:
        markup = web.getHtml(url)
        self._parser = web.getHtmlParser(markup)

    def select_move_rows(self) -> list[MoveRowTag]:
        return [MoveRowTag(r) for r in self._parser.select("#moves > tbody > tr")]
