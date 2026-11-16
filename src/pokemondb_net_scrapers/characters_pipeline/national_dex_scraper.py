from pokemondb_net_scrapers.characters_pipeline.html import NationalDexPage
from pokemondb_net_scrapers.models.character_seed import CharacterSeed


class NationalDexScraper:
    def __init__(self, url: str) -> None:
        self._page = NationalDexPage(url)

    def list_seed_characters(self) -> list[CharacterSeed]:
        seeds = []

        for generation, infocards in enumerate(self._page.select_infocards_by_generation(), start=1):
            for card in infocards:
                name = card.select_name()

                if not name:
                    continue

                seeds.append(CharacterSeed(
                    name=name,
                    generation=generation,
                    thumbnailUrl=card.select_image(),
                    pokemonId=card.select_pokemon_id(),
                    types=card.select_types(),
                ))

        return seeds
