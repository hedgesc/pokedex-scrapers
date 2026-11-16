from pokemondb_net_scrapers.characters_pipeline import html as html_module
from pokemondb_net_scrapers.characters_pipeline.character_moves_scraper import CharacterMovesScraper
from pokemondb_net_scrapers.characters_pipeline.character_scraper import CharacterScraper
from pokemondb_net_scrapers.characters_pipeline.national_dex_scraper import NationalDexScraper
from pokemondb_net_scrapers.models.character_seed import CharacterSeed


NATIONAL_DEX_HTML = """
<div class="infocard-list">
  <div class="infocard">
    <div class="infocard-lg-img"><a><span class="img-sprite" src="bulba.png"></span></a></div>
    <div class="infocard-lg-data"><small>#001</small><a class="ent-name">Bulbasaur</a></div>
    <span class="itype grass">Grass</span><span class="itype poison">Poison</span>
  </div>
</div>
<div class="infocard-list">
  <div class="infocard">
    <div class="infocard-lg-img"><a><span class="img-sprite" src="chiko.png"></span></a></div>
    <div class="infocard-lg-data"><small>#152</small><a class="ent-name">Chikorita</a></div>
    <span class="itype grass">Grass</span>
  </div>
</div>
"""

PANEL_HTML = """
<div id="tab-basic">
  <div class="grid-row"><div class="grid-col"><img src="bulba.png"></div></div>
  <div id="dex-stats"></div>
  <div class="resp-scroll">
    <table class="vitals-table">
      <tr><th>HP</th><td>45</td></tr>
      <tr><th>Attack</th><td>49</td></tr>
      <tr><th>Defense</th><td>49</td></tr>
      <tr><th>Sp. Atk</th><td>65</td></tr>
      <tr><th>Sp. Def</th><td>65</td></tr>
      <tr><th>Speed</th><td>45</td></tr>
      <tr><th>Total</th><td>318</td></tr>
    </table>
  </div>
  <div class="grid-col">
    <h2>Pokédex data</h2>
    <table class="vitals-table">
      <tr><th>Type</th><td><a>Grass</a><a>Poison</a></td></tr>
      <tr><th>Abilities</th><td><span><a>Overgrow</a></span></td></tr>
    </table>
  </div>
</div>
"""

DETAIL_HTML = f"""
<html><body>
<div class="tabset-basics">
  <span class="sv-tabs-tab-list">
    <a href="#tab-basic" class="sv-tabs-tab">Bulbasaur</a>
  </span>
</div>
{PANEL_HTML}
<div class="infocard-list-evo">
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Bulbasaur</a></div></div>
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Ivysaur</a></div></div>
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Venusaur</a></div></div>
</div>
</body></html>
"""

MOVES_HTML = """
<div class="tabset-moves-game">
  <span class="sv-tabs-tab-list">
    <a href="#tab-sword-shield" class="sv-tabs-tab">Sword/Shield</a>
  </span>
</div>
<div id="tab-sword-shield">
  <div class="grid-col">
    <div class="resp-scroll">
      <table class="data-table">
        <thead><tr><th><span class="sortwrap">Lv.</span></th></tr></thead>
        <tbody>
          <tr>
            <td>1</td>
            <td><a href="/move/tackle">Tackle</a></td>
            <td></td><td></td>
            <td>40</td>
            <td>100</td>
          </tr>
          <tr>
            <td>7</td>
            <td><a href="/move/vine-whip">Vine Whip</a></td>
            <td></td><td></td>
            <td>45</td>
            <td>100</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
"""


def test_national_dex_scraper_lists_seed_characters(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: NATIONAL_DEX_HTML)

    seeds = NationalDexScraper("https://example.com/pokedex/national").list_seed_characters()

    assert [seed.name for seed in seeds] == ["Bulbasaur", "Chikorita"]
    assert [seed.generation for seed in seeds] == [1, 2]
    assert seeds[0].nameId == "bulbasaur"
    assert seeds[0].pokemonId == "001"
    assert seeds[0].types == ["Grass", "Poison"]
    assert seeds[0].thumbnailUrl == "bulba.png"


def test_character_scraper_builds_base_form(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: DETAIL_HTML)
    seed = CharacterSeed("Bulbasaur", generation=1, pokemonId="0001", thumbnailUrl="thumb.png")

    character = CharacterScraper("https://example.com/pokedex/bulbasaur").build_character(seed)

    assert character.nameId == "bulbasaur"
    assert character.finalEvolutionId == "venusaur"
    assert character.hp == 45
    assert character.total == 318
    assert character.types == ["Grass", "Poison"]
    assert character.abilities == ["Overgrow"]
    assert character.imageUrl1 == "bulba.png"
    assert character.imageUrl2 == character.serebiiNetImage()


def test_character_moves_scraper_builds_rows_for_each_game_tab(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: MOVES_HTML)
    seed = CharacterSeed("Bulbasaur", characterId=1)

    rows = CharacterMovesScraper("https://example.com/pokedex/bulbasaur/moves/8").build_character_moves(seed)

    assert [(row.moveName, row.learnedById, row.isSuggested) for row in rows] == [
        ("Vine Whip", "7", True),
        ("Tackle", "1", True),
    ]
    assert rows[0].dexNameId == "sword-shield"
    assert rows[0].generation == 8
    assert rows[0].characterId == 1
