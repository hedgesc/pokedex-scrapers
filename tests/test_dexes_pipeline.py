from pokemondb_net_scrapers.dexes_pipeline import html as html_module
from pokemondb_net_scrapers.dexes_pipeline.dex_scraper import DexScraper


DEX_HTML = """
<div class="infocard-list">
  <div class="infocard">
    <div class="infocard-lg-img"><a><span class="img-sprite" src="bulba.png"></span></a></div>
    <div class="infocard-lg-data"><small>#0001</small><a class="ent-name">Bulbasaur</a></div>
  </div>
</div>
"""


def test_dex_scraper_lists_dex_characters(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: DEX_HTML)

    rows = DexScraper("https://example.com/pokedex/game/red-blue-yellow").list_dex_characters("red-blue-yellow")

    assert len(rows) == 1
    assert rows[0].nameId == "bulbasaur"
    assert rows[0].pokemonId == "0001"
    assert rows[0].thumbnailImage == "bulba.png"
    assert rows[0].dexId == "red-blue-yellow"
