"""InfocardTag: shared HTML-selector knowledge for pokemondb.net's
"infocard" grid markup (a repeated <div class="infocard"> card - thumbnail,
pokedex number, name, types).

This grid is the whole page for a dex listing and is grouped by generation
on the national dex listing. characters_pipeline and dexes_pipeline both
wrap this same card shape. It lives here so neither pipeline reaches into
the other's html module to reuse it.
"""

from bs4 import Tag


class InfocardTag:
    def __init__(self, tag: Tag) -> None:
        self._tag = tag

    def select_name(self) -> str:
        name = self._tag.select_one(".ent-name")
        return name.get_text() if name is not None else ""

    def select_image(self) -> str:
        img = self._tag.select_one(".infocard-lg-img > a > .img-sprite")

        if img is None:
            return ""

        if img.has_attr("src"):
            return str(img.attrs["src"])

        if img.has_attr("data-src"):
            return str(img.attrs["data-src"])

        return ""

    def select_pokemon_id(self) -> str:
        small = self._tag.select_one(".infocard-lg-data > small")
        return small.get_text().replace("#", "") if small is not None else ""

    def select_types(self) -> list[str]:
        return [t.get_text() for t in self._tag.select(".itype")]
