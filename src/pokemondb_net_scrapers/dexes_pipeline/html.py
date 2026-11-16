from pokemondb_net_scrapers.shared.infocard_html import InfocardTag
from scraping_shared import web


class DexPage:
    def __init__(self, url: str) -> None:
        markup = web.getHtml(url)
        self._parser = web.getHtmlParser(markup)

    def select_infocards(self) -> list[InfocardTag]:
        return [InfocardTag(c) for c in self._parser.select(".infocard-list > .infocard")]
