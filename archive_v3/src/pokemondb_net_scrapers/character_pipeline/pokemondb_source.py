from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.character import Character
from pokemondb_net_scrapers.utils import parsing

from ._pokemondb_html import CharacterDetailPage, NationalDexPage


class PokemonDbCharacterSource:
    """CharacterSource backed by pokemondb.net's national dex listing page
    and each species' detail page. All markup/selector knowledge lives in
    _pokemondb_html.py - this class only orchestrates it into Characters.
    """

    def __init__(self, national_dex_url: str | None = None) -> None:
        self._national_dex_url = national_dex_url or settings.national_dex_url

    def list_seed_characters(self) -> list[Character]:
        page = NationalDexPage(self._national_dex_url)
        seeds = []

        for generation, infocards in enumerate(page.select_infocards_by_generation(), start=1):
            for card in infocards:
                name = card.select_name()

                if not name:
                    continue

                seed = Character(name)
                seed.generation = generation
                seed.thumbnailUrl = card.select_image()
                seed.pokemonId = card.select_pokemon_id()
                seed.types = card.select_types()
                seeds.append(seed)

        return seeds

    def build_character_variants(self, seed: Character) -> list[Character]:
        page = CharacterDetailPage(seed.getDetailUrl())
        variants = []

        for tab, panel in page.select_tabs():
            variant = seed.model_copy(deep=True)

            if tab.is_alternate_form():
                # Alternate forms (Mega evolutions, regional forms, etc.) share
                # their base species' nameId on the site, but every returned
                # Character needs a nameId unique across the whole run since
                # that's what callers cache by - so give it one derived from
                # the base nameId plus the form's own tab name.
                variant.isAlternateForm = True
                variant.alternateName = tab.name
                variant.nameId = f"{seed.nameId}-{parsing.convertToId(tab.name)}"
                variant.imageUrl2 = ""
            else:
                final_evolution = page.select_final_evolution_name_id()

                if final_evolution:
                    variant.finalEvolutionId = final_evolution

                variant.imageUrl2 = variant.serebiiNetImage()

            variant.imageUrl1 = panel.select_image()
            variant.setBaseStats(panel.select_stats())
            variant.types = panel.select_types()
            variant.abilities = panel.select_abilities()

            variants.append(variant)

        return variants
