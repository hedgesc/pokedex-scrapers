from bs4 import BeautifulSoup

from pokemondb_net_scrapers.shared.infocard_html import InfocardTag


def make_tag(html):
    return BeautifulSoup(html, "html.parser").find()


def test_infocard_tag_select_name():
    card = make_tag('<div class="infocard"><a class="ent-name">Bulbasaur</a></div>')
    assert InfocardTag(card).select_name() == "Bulbasaur"


def test_infocard_tag_select_name_missing_returns_empty_string():
    card = make_tag('<div class="infocard"></div>')
    assert InfocardTag(card).select_name() == ""


def test_infocard_tag_select_image_prefers_src_over_data_src():
    card = make_tag(
        '<div class="infocard"><div class="infocard-lg-img"><a>'
        '<span class="img-sprite" src="bulba.png" data-src="lazy.png"></span></a></div></div>'
    )
    assert InfocardTag(card).select_image() == "bulba.png"


def test_infocard_tag_select_image_falls_back_to_data_src():
    card = make_tag(
        '<div class="infocard"><div class="infocard-lg-img"><a>'
        '<span class="img-sprite" data-src="lazy.png"></span></a></div></div>'
    )
    assert InfocardTag(card).select_image() == "lazy.png"


def test_infocard_tag_select_image_missing_returns_empty_string():
    card = make_tag('<div class="infocard"></div>')
    assert InfocardTag(card).select_image() == ""


def test_infocard_tag_select_pokemon_id_strips_hash():
    card = make_tag('<div class="infocard"><div class="infocard-lg-data"><small>#001</small></div></div>')
    assert InfocardTag(card).select_pokemon_id() == "001"


def test_infocard_tag_select_types():
    card = make_tag(
        '<div class="infocard"><span class="itype grass">Grass</span>'
        '<span class="itype poison">Poison</span></div>'
    )
    assert InfocardTag(card).select_types() == ["Grass", "Poison"]
