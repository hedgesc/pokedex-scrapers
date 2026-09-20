import logging

from bs4 import Tag

from pokemondb_net_scrapers.scrapers.tags import CharacterTabPanelTag, CharacterTabTag, InfocardListTag
from pokemondb_net_scrapers.utils import parsing, web

logger = logging.getLogger(__name__)

class NationalParser:
    def __init__(
        self,
		url: str
    ) -> None:
        markup = web.getHtml(url)
        self._parser = web.getHtmlParser(markup)
        
    def selectInfocardListTags(self) -> list[InfocardListTag]:
        return [InfocardListTag(t) for t in self._parser.select('.infocard-list')]


class CharacterParser:
    def __init__(self, url: str) -> None:
        markup = web.getHtml(url)
        self._parser = web.getHtmlParser(markup)

    def selectTabPanels(self) -> list[tuple[CharacterTabTag, CharacterTabPanelTag]]:
        result = []
        tabs = self._parser.select(".tabset-basics > .sv-tabs-tab-list > .sv-tabs-tab")

        for index, tab in enumerate(tabs):
            panel = self._parser.select_one(tab["href"])

            if panel is None:
                continue

            result.append((CharacterTabTag(index, tab), CharacterTabPanelTag(panel)))

        return result

    def selectEvolutions(self) -> list[str]:
        evolutions = []
        evo_list = self._parser.select_one(".infocard-list-evo")
            
        if not evo_list is None:
            cards = evo_list.find_all('div', {'class': ['infocard']})
    
            for c in cards:
                name = c.select_one('.infocard-lg-data').select_one('a.ent-name').get_text()
                name_id = parsing.convertToId(name)
                evolutions.append(name_id)
    
        return evolutions
