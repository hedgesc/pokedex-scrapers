import pytest
from bs4 import BeautifulSoup

from pokemondb_net_scrapers.character_pipeline import _pokemondb_html as html_module
from pokemondb_net_scrapers.character_pipeline._pokemondb_html import (
    CharacterDetailPage,
    CharacterTabPanelTag,
    InfocardTag,
    NationalDexPage,
)
from pokemondb_net_scrapers.character_pipeline.builder import CharacterBuilder
from pokemondb_net_scrapers.character_pipeline.pokemondb_source import PokemonDbCharacterSource
from pokemondb_net_scrapers.character_pipeline.source import CharacterSource
from pokemondb_net_scrapers.config import CacheConfig
from pokemondb_net_scrapers.interfaces import CacheClient
from pokemondb_net_scrapers.models.character import Character


def make_tag(html):
    return BeautifulSoup(html, "html.parser").find()


def make_character(name, **overrides):
    c = Character(name)

    for k, v in overrides.items():
        setattr(c, k, v)

    return c


# --- CharacterBuilder --------------------------------------------------

class FakeCharacterSource:
    def __init__(self, seeds, variants_by_name_id):
        self._seeds = seeds
        self._variants_by_name_id = variants_by_name_id

    def list_seed_characters(self):
        return self._seeds

    def build_character_variants(self, seed):
        return self._variants_by_name_id[seed.nameId]


class RecordingCacheClient:
    def __init__(self, fail_for=frozenset()):
        self.calls = []
        self._fail_for = fail_for

    def set(self, key, value, ttl=None):
        if key in self._fail_for:
            raise RuntimeError("cache unavailable")

        self.calls.append((key, value, ttl))

    def get(self, key):
        for k, v, _ in self.calls:
            if k == key:
                return v

        return None


def make_builder(seeds, variants_by_name_id, cache=None, cache_config=None):
    source = FakeCharacterSource(seeds, variants_by_name_id)
    cache = cache if cache is not None else RecordingCacheClient()
    return CharacterBuilder(source, cache, cache_config), cache


def test_fake_character_source_satisfies_character_source_protocol():
    assert isinstance(FakeCharacterSource([], {}), CharacterSource)


def test_recording_cache_client_satisfies_cache_client_protocol():
    assert isinstance(RecordingCacheClient(), CacheClient)


def test_build_returns_list_of_characters():
    builder, _ = make_builder(
        seeds=[make_character("Bulbasaur")],
        variants_by_name_id={"bulbasaur": [make_character("Bulbasaur")]},
    )

    result = builder.build()

    assert isinstance(result, list)
    assert all(isinstance(c, Character) for c in result)


def test_build_assigns_sequential_ids_across_seeds_and_variants():
    bulbasaur = make_character("Bulbasaur")
    pikachu = make_character("Pikachu")

    builder, _ = make_builder(
        seeds=[bulbasaur, pikachu],
        variants_by_name_id={
            "bulbasaur": [make_character("Bulbasaur")],
            "pikachu": [
                make_character("Pikachu"),
                make_character("Pikachu", nameId="pikachu-alolan-form", isAlternateForm=True),
            ],
        },
    )

    result = builder.build()

    assert [c.characterId for c in result] == [1, 2, 3]


def test_build_caches_name_id_to_character_id_with_configured_prefix():
    builder, cache = make_builder(
        seeds=[make_character("Bulbasaur")],
        variants_by_name_id={"bulbasaur": [make_character("Bulbasaur", nameId="bulbasaur")]},
        cache_config=CacheConfig(characters_key_prefix="chars:"),
    )

    builder.build()

    assert cache.calls == [("chars:bulbasaur", "1", None)]


def test_build_passes_ttl_from_cache_config():
    builder, cache = make_builder(
        seeds=[make_character("Bulbasaur")],
        variants_by_name_id={"bulbasaur": [make_character("Bulbasaur")]},
        cache_config=CacheConfig(ttl_seconds=3600),
    )

    builder.build()

    assert cache.calls[0][2] == 3600


def test_build_swallows_cache_errors_by_default():
    builder, _ = make_builder(
        seeds=[make_character("Bulbasaur")],
        variants_by_name_id={"bulbasaur": [make_character("Bulbasaur")]},
        cache=RecordingCacheClient(fail_for={"characters:bulbasaur"}),
    )

    result = builder.build()

    assert len(result) == 1


def test_build_raises_on_cache_error_when_configured():
    builder, _ = make_builder(
        seeds=[make_character("Bulbasaur")],
        variants_by_name_id={"bulbasaur": [make_character("Bulbasaur")]},
        cache=RecordingCacheClient(fail_for={"characters:bulbasaur"}),
        cache_config=CacheConfig(raise_on_cache_error=True),
    )

    with pytest.raises(RuntimeError):
        builder.build()


# --- _pokemondb_html: NationalDexPage ------------------------------------
#
# InfocardTag itself is shared cross-pipeline now (see
# pokemondb_net_scrapers.shared.infocard_html and
# tests/test_shared_infocard_html.py) - it's still imported here because
# NationalDexPage returns it, but its own selector behavior is no longer
# tested from this file.

NATIONAL_DEX_HTML = """
<div class="infocard-list">
  <div class="infocard">
    <div class="infocard-lg-img"><a><span class="img-sprite" src="bulba.png"></span></a></div>
    <div class="infocard-lg-data"><small>#001</small><a class="ent-name">Bulbasaur</a></div>
    <span class="itype grass">Grass</span><span class="itype poison">Poison</span>
  </div>
  <div class="infocard">
    <div class="infocard-lg-img"><a><span class="img-sprite" src="ivy.png"></span></a></div>
    <div class="infocard-lg-data"><small>#002</small><a class="ent-name">Ivysaur</a></div>
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


def test_national_dex_page_groups_infocards_by_generation(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: NATIONAL_DEX_HTML)

    page = NationalDexPage("https://example.com/pokedex/national")
    by_gen = page.select_infocards_by_generation()

    assert [len(cards) for cards in by_gen] == [2, 1]
    assert by_gen[0][0].select_name() == "Bulbasaur"
    assert by_gen[0][1].select_name() == "Ivysaur"
    assert by_gen[1][0].select_name() == "Chikorita"


# --- _pokemondb_html: CharacterTabPanelTag -------------------------------

PANEL_HTML_BASE = """
<div id="tab-basic">
  <div class="grid-row"><div class="grid-col"><img src="pikachu.png"></div></div>
  <div id="dex-stats"></div>
  <div class="resp-scroll">
    <table class="vitals-table">
      <tr><th>HP</th><td>35</td></tr>
      <tr><th>Attack</th><td>55</td></tr>
      <tr><th>Defense</th><td>40</td></tr>
      <tr><th>Sp. Atk</th><td>50</td></tr>
      <tr><th>Sp. Def</th><td>50</td></tr>
      <tr><th>Speed</th><td>90</td></tr>
      <tr><th>Total</th><td>320</td></tr>
    </table>
  </div>
  <div class="grid-col">
    <h2>Pokédex data</h2>
    <table class="vitals-table">
      <tr><th>Type</th><td><a>Electric</a></td></tr>
      <tr><th>Abilities</th><td><span><a>Static</a></span><span><a>Lightning Rod</a></span></td></tr>
    </table>
  </div>
</div>
"""

PANEL_HTML_ALT = """
<div id="tab-alolan">
  <div class="grid-row"><div class="grid-col"><img src="pikachu-alolan.png"></div></div>
  <div id="dex-stats"></div>
  <div class="resp-scroll">
    <table class="vitals-table">
      <tr><th>HP</th><td>35</td></tr>
      <tr><th>Attack</th><td>60</td></tr>
      <tr><th>Defense</th><td>40</td></tr>
      <tr><th>Sp. Atk</th><td>50</td></tr>
      <tr><th>Sp. Def</th><td>50</td></tr>
      <tr><th>Speed</th><td>95</td></tr>
      <tr><th>Total</th><td>330</td></tr>
    </table>
  </div>
  <div class="grid-col">
    <h2>Pokédex data</h2>
    <table class="vitals-table">
      <tr><th>Type</th><td><a>Electric</a></td></tr>
      <tr><th>Abilities</th><td><span><a>Static</a></span></td></tr>
    </table>
  </div>
</div>
"""


def test_character_tab_panel_tag_select_image():
    panel = make_tag(PANEL_HTML_BASE)
    assert CharacterTabPanelTag(panel).select_image() == "pikachu.png"


def test_character_tab_panel_tag_select_stats():
    panel = make_tag(PANEL_HTML_BASE)
    stats = CharacterTabPanelTag(panel).select_stats()

    assert stats.hp == 35
    assert stats.attack == 55
    assert stats.defense == 40
    assert stats.specialAttack == 50
    assert stats.specialDefense == 50
    assert stats.speed == 90
    assert stats.total == 320


def test_character_tab_panel_tag_select_types_and_abilities():
    tag = CharacterTabPanelTag(make_tag(PANEL_HTML_BASE))

    assert tag.select_types() == ["Electric"]
    assert tag.select_abilities() == ["Static", "Lightning Rod"]


def test_character_tab_panel_tag_missing_pokedex_data_table_returns_empty_lists():
    tag = CharacterTabPanelTag(make_tag('<div id="tab-basic"></div>'))

    assert tag.select_types() == []
    assert tag.select_abilities() == []


# --- _pokemondb_html: CharacterDetailPage --------------------------------

DETAIL_PAGE_HTML = f"""
<html><body>
<div class="tabset-basics">
  <span class="sv-tabs-tab-list">
    <a href="#tab-basic" class="sv-tabs-tab">Pikachu</a>
    <a href="#tab-alolan" class="sv-tabs-tab">Alolan Form</a>
  </span>
</div>
{PANEL_HTML_BASE}
{PANEL_HTML_ALT}
<div class="infocard-list-evo">
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Pichu</a></div></div>
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Pikachu</a></div></div>
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Raichu</a></div></div>
</div>
</body></html>
"""

SINGLE_TAB_DETAIL_HTML = f"""
<html><body>
<div class="tabset-basics">
  <span class="sv-tabs-tab-list">
    <a href="#tab-basic" class="sv-tabs-tab">Pikachu</a>
  </span>
</div>
{PANEL_HTML_BASE}
<div class="infocard-list-evo">
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Pichu</a></div></div>
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Pikachu</a></div></div>
  <div class="infocard"><div class="infocard-lg-data"><a class="ent-name">Raichu</a></div></div>
</div>
</body></html>
"""


def test_character_detail_page_select_tabs(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: DETAIL_PAGE_HTML)

    tabs = CharacterDetailPage("https://example.com/pokedex/pikachu").select_tabs()

    assert len(tabs) == 2
    assert tabs[0][0].is_alternate_form() is False
    assert tabs[0][0].name == "Pikachu"
    assert tabs[1][0].is_alternate_form() is True
    assert tabs[1][0].name == "Alolan Form"
    assert tabs[1][1].select_image() == "pikachu-alolan.png"


def test_character_detail_page_select_final_evolution_name_id(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: DETAIL_PAGE_HTML)

    page = CharacterDetailPage("https://example.com/pokedex/pikachu")

    assert page.select_final_evolution_name_id() == "raichu"


def test_character_detail_page_select_final_evolution_name_id_missing_returns_empty_string(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: "<html><body></body></html>")

    page = CharacterDetailPage("https://example.com/pokedex/eevee")

    assert page.select_final_evolution_name_id() == ""


# --- PokemonDbCharacterSource --------------------------------------------

def test_pokemondb_source_satisfies_character_source_protocol():
    assert isinstance(PokemonDbCharacterSource(), CharacterSource)


def test_pokemondb_source_list_seed_characters(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: NATIONAL_DEX_HTML)

    seeds = PokemonDbCharacterSource(national_dex_url="https://example.com/pokedex/national").list_seed_characters()

    assert [s.name for s in seeds] == ["Bulbasaur", "Ivysaur", "Chikorita"]
    assert [s.generation for s in seeds] == [1, 1, 2]
    assert seeds[0].nameId == "bulbasaur"
    assert seeds[0].pokemonId == "001"
    assert seeds[0].types == ["Grass", "Poison"]
    assert seeds[0].thumbnailUrl == "bulba.png"


def test_pokemondb_source_build_character_variants_single_form(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: SINGLE_TAB_DETAIL_HTML)

    variants = PokemonDbCharacterSource().build_character_variants(make_character("Pikachu"))

    assert len(variants) == 1
    variant = variants[0]
    assert variant.isAlternateForm is False
    assert variant.nameId == "pikachu"
    assert variant.finalEvolutionId == "raichu"
    assert variant.imageUrl2 == variant.serebiiNetImage()
    assert variant.hp == 35
    assert variant.speed == 90
    assert variant.abilities == ["Static", "Lightning Rod"]


def test_pokemondb_source_build_character_variants_alternate_form_gets_distinct_name_id(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: DETAIL_PAGE_HTML)

    variants = PokemonDbCharacterSource().build_character_variants(make_character("Pikachu"))

    assert len(variants) == 2
    base, alt = variants

    assert base.nameId == "pikachu"
    assert base.isAlternateForm is False

    assert alt.nameId == "pikachu-alolan-form"
    assert alt.isAlternateForm is True
    assert alt.alternateName == "Alolan Form"
    # alternate forms don't carry a final-evolution id or the serebii fallback image
    assert alt.finalEvolutionId == ""
    assert alt.imageUrl2 == ""
    # proves each variant gets its own detail-panel data, not a shared copy
    assert alt.speed == 95
    assert alt.abilities == ["Static"]
