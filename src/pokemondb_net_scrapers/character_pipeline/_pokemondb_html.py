"""Private HTML-selector knowledge for PokemonDbCharacterSource.

Every BeautifulSoup selector pokemondb.net's markup requires for the
character detail/national-dex pages lives here, and only here (the
InfocardTag it also uses is shared cross-pipeline - see
pokemondb_net_scrapers.shared.infocard_html - so it isn't defined here even
though this module was its original home). If a page's markup changes, this
is the only module that should need to change - pokemondb_source.py just
orchestrates these wrapper classes.
"""

from bs4 import Tag

from pokemondb_net_scrapers.models.character import BaseStats
from pokemondb_net_scrapers.shared.infocard_html import InfocardTag
from pokemondb_net_scrapers.utils import parsing, web

__all__ = [
    "CharacterDetailPage",
    "CharacterTabPanelTag",
    "CharacterTabTag",
    "InfocardTag",
    "NationalDexPage",
]


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
