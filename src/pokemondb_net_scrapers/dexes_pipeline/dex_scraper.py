from pokemondb_net_scrapers.dexes_pipeline.html import DexPage
from pokemondb_net_scrapers.models.dex_character import DexCharacter
from pokemondb_net_scrapers.utils import parsing


class DexScraper:
    def __init__(self, url: str) -> None:
        self._page = DexPage(url)

    def list_dex_characters(self, dex_id: str) -> list[DexCharacter]:
        result = []

        for card in self._page.select_infocards():
            name = card.select_name()

            if not name:
                continue

            result.append(DexCharacter(
                parsing.convertToId(name),
                card.select_pokemon_id(),
                card.select_image(),
                dexId=dex_id,
            ))

        return result
