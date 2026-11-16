"""HTML-selector knowledge for pokemondb.net character pages.

NationalDexPage, CharacterDetailPage, and CharacterMovesPage own every
BeautifulSoup selector those pages need. InfocardTag lives in
pokemondb_net_scrapers.shared.infocard_html because dex listings use the
same card markup.
"""

from bs4 import Tag

from pokemondb_net_scrapers.models.character import BaseStats
from pokemondb_net_scrapers.models.game_move import GameMove
from pokemondb_net_scrapers.shared.infocard_html import InfocardTag
from pokemondb_net_scrapers.utils import parsing
from scraping_shared import web

__all__ = [
    "CharacterDetailPage",
    "CharacterMovesPage",
    "CharacterTabPanelTag",
    "CharacterTabTag",
    "InfocardTag",
    "NationalDexPage",
]

_LEARNED_BY_HEADERS = ("Lv.", "HM", "TM")


class NationalDexPage:
    def __init__(self, url: str) -> None:
        markup = web.getHtml(url)
        self._parser = web.getHtmlParser(markup)

    def select_infocards_by_generation(self) -> list[list[InfocardTag]]:
        """One list of InfocardTags per generation section, in generation order."""
        gen_lists = self._parser.select(".infocard-list")
        return [[InfocardTag(c) for c in gen_list.select(".infocard")] for gen_list in gen_lists]


class CharacterTabTag:
    def __init__(self, index: int, tag: Tag) -> None:
        self.index = index
        self.name = tag.get_text()
        self.panel_selector = tag["href"]

    def is_alternate_form(self) -> bool:
        return self.index > 0


class CharacterTabPanelTag:
    def __init__(self, tag: Tag) -> None:
        self._tag = tag

    def select_image(self) -> str:
        grid_row = self._tag.select_one(".grid-row")

        if grid_row is None:
            return ""

        grid_col = grid_row.select_one(".grid-col")

        if grid_col is None:
            return ""

        img_tag = grid_col.select_one("img")

        if img_tag is None:
            return ""

        return img_tag["src"]

    def select_stats(self) -> BaseStats:
        stats = BaseStats()
        rows = self._tag.select("#dex-stats ~ .resp-scroll > .vitals-table tr")

        for r in rows:
            h = r.select_one("th").get_text()
            n = r.select("td")[0].get_text()

            if h == "HP":
                stats.hp = int(n)
            elif h == "Attack":
                stats.attack = int(n)
            elif h == "Defense":
                stats.defense = int(n)
            elif h == "Sp. Atk":
                stats.specialAttack = int(n)
            elif h == "Sp. Def":
                stats.specialDefense = int(n)
            elif h == "Speed":
                stats.speed = int(n)
            elif h == "Total":
                stats.total = int(n)

        return stats

    def select_types(self) -> list[str]:
        row = self._find_vitals_table_row("Pokédex data", "Type")
        return [a.get_text() for a in row.select("td > a")] if row is not None else []

    def select_abilities(self) -> list[str]:
        row = self._find_vitals_table_row("Pokédex data", "Abilities")
        return [a.get_text() for a in row.select("td > span > a")] if row is not None else []

    def _find_vitals_table(self, table_name: str) -> Tag | None:
        for col in self._tag.select(".grid-col"):
            h_tag = col.select_one("h2")

            if h_tag is not None and h_tag.get_text() == table_name:
                return col.select_one(".vitals-table")

        return None

    def _find_vitals_table_row(self, table_name: str, row_title: str) -> Tag | None:
        table = self._find_vitals_table(table_name)

        if table is None:
            return None

        for row in table.select("tr"):
            h_tag = row.select_one("th")

            if h_tag is not None and h_tag.get_text() == row_title:
                return row

        return None


class CharacterDetailPage:
    def __init__(self, url: str) -> None:
        markup = web.getHtml(url)
        self._parser = web.getHtmlParser(markup)

    def select_tabs(self) -> list[tuple[CharacterTabTag, CharacterTabPanelTag]]:
        result = []
        tabs = self._parser.select(".tabset-basics > .sv-tabs-tab-list > .sv-tabs-tab")

        for index, tab in enumerate(tabs):
            panel = self._parser.select_one(tab["href"])

            if panel is None:
                continue

            result.append((CharacterTabTag(index, tab), CharacterTabPanelTag(panel)))

        return result

    def select_final_evolution_name_id(self) -> str:
        """nameId of the last stage in this species' evolution line, or ''
        if the species has no evolution chart (e.g. it doesn't evolve)."""
        evo_list = self._parser.select_one(".infocard-list-evo")

        if evo_list is None:
            return ""

        cards = evo_list.find_all("div", {"class": ["infocard"]})

        if not cards:
            return ""

        last_name = cards[-1].select_one(".infocard-lg-data").select_one("a.ent-name").get_text()
        return parsing.convertToId(last_name)


class CharacterMovesPage:
    def __init__(self, url: str) -> None:
        markup = web.getHtml(url)
        self._parser = web.getHtmlParser(markup)

    def select_game_moves(self) -> list[tuple[str, list[GameMove]]]:
        """(game tab name, moves) for each game tab on a generation moves page."""
        result = []
        tabs = self._parser.select(".tabset-moves-game > .sv-tabs-tab-list > .sv-tabs-tab")

        for tab in tabs:
            panel = self._parser.select_one(tab["href"])

            if panel is None:
                continue

            result.append((tab.get_text(), _moves_in_panel(panel)))

        return result


def _moves_in_panel(panel: Tag) -> list[GameMove]:
    moves = []

    for table in panel.select(".grid-col > .resp-scroll > .data-table"):
        header = table.select_one("thead > tr > th > .sortwrap")

        if header is None:
            continue

        learned_by = header.get_text()

        if learned_by not in _LEARNED_BY_HEADERS:
            continue

        for row in table.select("tbody > tr"):
            columns = row.find_all("td")
            move_link = columns[1].find("a")
            move = GameMove(
                move_link.get_text(),
                move_link["href"].split("/")[-1],
                columns[4].get_text(),
                columns[5].get_text(),
            )
            move.setLearnedByInfo(learned_by, columns[0].get_text())
            moves.append(move)

    moves.sort(key=lambda move: (move.power, move.learnedById), reverse=True)
    return moves
