from pokemondb_net_scrapers.characters_pipeline.html import CharacterDetailPage
from pokemondb_net_scrapers.models.character import Character
from pokemondb_net_scrapers.models.character_seed import CharacterSeed


class CharacterScraper:
    def __init__(self, url: str) -> None:
        self._page = CharacterDetailPage(url)

    def build_character(self, seed: CharacterSeed) -> Character:
        character = Character(
            name=seed.name,
            nameId=seed.nameId,
            characterId=seed.characterId,
            pokemonId=seed.pokemonId,
            generation=seed.generation,
            thumbnailUrl=seed.thumbnailUrl,
            types=list(seed.types),
        )
        tabs = self._page.select_tabs()

        if not tabs:
            return character

        _tab, panel = tabs[0]
        final_evolution = self._page.select_final_evolution_name_id()

        if final_evolution:
            character.finalEvolutionId = final_evolution

        character.imageUrl2 = character.serebiiNetImage()
        character.imageUrl1 = panel.select_image()
        character.setBaseStats(panel.select_stats())
        types = panel.select_types()

        if types:
            character.types = types

        character.abilities = panel.select_abilities()
        return character
