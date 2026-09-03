import logging

from pokemondb_net_scrapers.scrapers.tags import InfocardTag
from pokemondb_net_scrapers.scrapers.parsers import CharacterParser, NationalParser
from pokemondb_net_scrapers.models.character import Character

from ..config import settings
from ..interfaces import CacheClient

logger = logging.getLogger(__name__)

class CharacterScraper:
    def __init__(
        self,
        cache_client: CacheClient
    ) -> None:
        self._cache = cache_client
        self._characters: list[Character] = []

        
    def run(self, characters: dict[str, Character]) -> None:
        if characters is None:
            self._scrape_all()
        else:
            self._characters = characters

        self._cache_characters()

        return {c.nameId: c for c in self._characters}


    def _cache_characters(self) -> None:
        for c in self._characters:
            try:
                self._cache.set(f"characters:{c.name_id}", c.id)
            except Exception:
                logger.exception("Failed to cache character %s", c.name)
                # decide: swallow, retry, or re-raise depending on how
                # critical the cache write is to the job's success


    def _scrape_all(self) -> None:
        self._scrape_national_page()
        self._scrape_character_page()


    def _scrape_national_page(self) -> None:
        national = NationalParser(settings.national_dex_url)
        infocard_lists = national.selectInfocardListTags()
        for index, list in enumerate(infocard_lists):
            infocards = list.selectInfocards()
            for card in infocards:
                base_char = self._createCharacterFromInfocard(card, index+1)
                self._characters.append(base_char)


    def _scrape_character_page(self) -> None:
        for i, c in enumerate(self._characters):
            detail_parser = CharacterParser(settings.character_dex_url(c.nameId))
            detail_tabs = detail_parser.selectTabPanels()
            
            for tab in detail_tabs:
                c.characterId = i + 1

                if tab[0].isAlternateForm():
                    c.isAlternateForm = True
                    c.alternateName = tab[0].text
                    c.imageUrl2 = ""
                else:
                    evolutions = detail_parser.selectEvolutions()
                    if len(evolutions) > 0:
                        c.finalEvolutionId = evolutions[-1]
                    c.imageUrl2 = c.serebiiNetImage()

                c.imageUrl1 = tab[1].selectImage()
                c.setBaseStats(tab[1].selectStats())
                c.types = tab[1].selectTypes()
                c.abilities = tab[1].selectAbilities()


    def _createCharacterFromInfocard(tag: InfocardTag, gen: int) -> Character:
        name = tag.selectName()
        result = Character(name)
        result.generation = gen
        result.thumbnailUrl = tag.selectImage()
        result.pokemonId = tag.selectPokemonId()
        result.types = tag.selectTypes()
        return result
