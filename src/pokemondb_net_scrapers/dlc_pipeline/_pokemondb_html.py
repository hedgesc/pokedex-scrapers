from pokemondb_net_scrapers.character_pipeline._pokemondb_html import InfocardTag
from pokemondb_net_scrapers.utils import web


class DlcDexPage:
    def __init__(self, url: str) -> None:
        markup = web.getHtml(url)
        self._parser = web.getHtmlParser(markup)

    def select_infocards(self) -> list[InfocardTag]:
        return [InfocardTag(c) for c in self._parser.select(".infocard-list > .infocard")]
