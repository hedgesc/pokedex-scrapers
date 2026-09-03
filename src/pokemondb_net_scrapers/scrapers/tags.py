import logging

from bs4 import Tag

from pokemondb_net_scrapers.models.character import BaseStats

logger = logging.getLogger(__name__)

class InfocardTag:
	def __init__(self, tag: Tag) -> None:
		self._tag = tag

	def selectImage(self) -> str:
		img = self._tag.select_one(".infocard-lg-img > a > .img-sprite")

		if img is None:
			return ""

		if img.has_attr("src"):
			return str(img.attrs["src"])

		if img.has_attr("data-src"):
			return str(img.attrs["data-src"])

		return ""

	def selectPokemonId(self) -> str:
		small = self._tag.select_one(".infocard-lg-data > small")

		if small is None:
			return ""

		return small.get_text().replace("#", "")

	def selectName(self) -> str:
		name = self._tag.select_one(".ent-name")

		if name is None:
			return ""

		return name.get_text()

	def selectTypes(self) -> list[str]:
		types = []

		for t in self._tag.select('.itype'):
			types.append(t.get_text())

		return types


class InfocardListTag:
    def __init__(self, tag: Tag) -> None:
        self._tag = tag

    def selectInfocards(self) -> list[InfocardTag]:
        return [InfocardTag(c) for c in self._tag.select('.infocard')]


class CharacterTabTag:
  def __init__(self, index: int, tag: Tag):
    self.index = index
    self.text: str = tag.get_text()

  def isAlternateForm(self):
    return self.index > 0


class CharacterTabPanelTag:
	def __init__(self, tag: Tag) -> None:
		self._tag = tag
		self._vitals_row: Tag = None
		self._vitals_table: Tag = None

	def selectImage(self) -> str:
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

	def selectStats(self) -> BaseStats:
		stats = BaseStats()
		rows = self._tag.select('#dex-stats ~ .resp-scroll > .vitals-table tr')

		for r in rows:
			h = r.select_one('th').get_text()
			n = r.select('td')[0].get_text()

			if(h == 'HP'):
				stats.hp = int(n)
			elif(h == 'Attack'):
				stats.attack = int(n)
			elif(h == 'Defense'):
				stats.defense = int(n)
			elif(h == 'Sp. Atk'):
				stats.specialAttack = int(n)
			elif(h == 'Sp. Def'):
				stats.specialDefense = int(n)
			elif(h == 'Speed'):
				stats.speed = int(n)
			elif(h == 'Total'):
				stats.total = int(n)

		return stats


	def selectTypes(self) -> list[str]:
		row = self._findVitalsTableRow("Pokédex data", "Type")

		if row is not None:
			return [a.get_text() for a in row.select("td > a")]

		return []


	def selectAbilities(self) -> list[str]:
		row = self._findVitalsTableRow("Pokédex data", "Abilities")

		if row is not None:
			return [a.get_text() for a in row.select("td > span > a")]

		return []


	def _findVitalsTable(self, table_name) -> Tag:
		cols = self._tag.select(".grid-col")
		
		for c in cols:
			h_tag = c.select_one("h2")
			
			if h_tag is None:
				continue

			if h_tag.get_text() == table_name:
				return c.select_one(".vitals-table")

		return None


	def _findVitalsTableRow(self, table_name, row_title) -> Tag:
		table = self._findVitalsTable(table_name)

		if table is None:
			return None

		rows = table.select("tr")

		for r in rows:
			h_tag = r.select_one("th")

			if h_tag is None:
				continue

			if h_tag.get_text() == row_title:
				return r

		return None