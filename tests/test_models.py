from bs4 import BeautifulSoup

from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.character import BaseStats, Character, CharacterTab, DexMovesTab
from pokemondb_net_scrapers.models.character_dex_move import CharacterDexMove
from pokemondb_net_scrapers.models.dex import Dex
from pokemondb_net_scrapers.models.dex_character import DexCharacter
from pokemondb_net_scrapers.models.dex_move import DexMove
from pokemondb_net_scrapers.models.dlc import Dlc
from pokemondb_net_scrapers.models.dlc_character import DlcCharacter
from pokemondb_net_scrapers.models.game import Game
from pokemondb_net_scrapers.models.move import Move
from pokemondb_net_scrapers.services import csv_exporter


def makeTag(html):
	return BeautifulSoup(html, "html.parser").find()


def makeCharacter(**overrides):
	c = Character("Bulbasaur")
	c.characterId = 1
	c.pokemonId = "0001"
	c.generation = 1
	c.total = 318
	c.hp = 45
	c.attack = 49
	c.defense = 49
	c.specialAttack = 65
	c.specialDefense = 65
	c.speed = 45
	c.nameId = "bulbasaur"
	c.alternateName = ""
	c.types = ["Grass", "Poison"]
	c.abilities = ["Overgrow", "Chlorophyll"]
	c.finalEvolutionId = "venusaur"
	c.isVisible = True
	c.thumbnailUrl = "thumb.png"
	c.imageUrl1 = "img1.png"
	c.imageUrl2 = "img2.png"

	for k, v in overrides.items():
		setattr(c, k, v)

	return c


# --- Character -------------------------------------------------------------

def test_character_defaults():
	c = Character("Bulbasaur")
	assert c.abilities == []
	assert c.thumbnailUrl == ""
	assert c.imageUrl1 == ""
	assert c.imageUrl2 == ""
	assert c.isVisible is True


def test_character_model_dump_default_uses_field_names():
	c = makeCharacter()
	dumped = c.model_dump()

	assert dumped["characterId"] == 1
	assert dumped["imageUrl1"] == "img1.png"
	assert dumped["imageUrl2"] == "img2.png"


def test_character_model_dump_by_alias_uses_snake_case():
	c = makeCharacter()
	dumped = c.model_dump(by_alias=True)

	assert dumped["character_id"] == 1
	assert dumped["pokemon_id"] == "0001"
	assert dumped["special_attack"] == 65
	assert dumped["special_defense"] == 65
	assert dumped["name_id"] == "bulbasaur"
	assert dumped["alternate_name"] == ""
	assert dumped["final_evolution_id"] == "venusaur"
	assert dumped["is_visible"] is True
	assert dumped["thumbnail_url"] == "thumb.png"
	# to_snake would otherwise produce image_url_1/image_url_2 - these are
	# explicitly overridden to match csv_exporter's header columns.
	assert dumped["image_url1"] == "img1.png"
	assert dumped["image_url2"] == "img2.png"


def test_character_model_dump_by_alias_matches_csv_exporter_header():
	c = makeCharacter()
	dumped = c.model_dump(by_alias=True)

	header_columns = csv_exporter.getCsvHeader(Character).strip().split(",")

	for column in header_columns:
		assert column in dumped


def test_character_populate_by_name_allows_construction_by_alias():
	c = Character.model_validate({"name": "Pikachu", "character_id": 25, "image_url1": "a.png"})

	assert c.characterId == 25
	assert c.imageUrl1 == "a.png"


def test_character_to_csv_string_with_multiple_types_and_abilities():
	c = makeCharacter()
	assert c.toCsvString() == (
		'1,0001,1,"Bulbasaur",318,45,49,49,65,65,45,bulbasaur,,'
		'"{Grass,Poison}","{Overgrow,Chlorophyll}",venusaur,t,'
		'"thumb.png","img1.png","img2.png"\n'
	)


def test_character_to_csv_string_with_single_type_and_ability():
	c = makeCharacter(types=["Grass"], abilities=["Overgrow"])
	assert '"{Grass}"' in c.toCsvString()
	assert '"{Overgrow}"' in c.toCsvString()


def test_character_to_csv_string_with_empty_types():
	c = makeCharacter(types=[])
	assert '"{}"' in c.toCsvString()


def test_character_to_csv_string_with_empty_abilities():
	c = makeCharacter(types=["Grass"], abilities=[])
	assert '"{}"' in c.toCsvString()


def test_character_get_is_visible():
	c = makeCharacter()
	c.isVisible = True
	assert c.getIsVisible() == "t"
	c.isVisible = False
	assert c.getIsVisible() == "f"


def test_character_get_detail_url():
	c = makeCharacter(nameId="pikachu")
	assert c.getDetailUrl() == settings.base_dex_url + "pikachu"


def test_character_serebii_net_image():
	c = makeCharacter(pokemonId="0025")
	assert c.serebiiNetImage() == "https://www.serebii.net/pokemon/art/0025.png"


def test_character_set_base_stats():
	stats = BaseStats()
	stats.hp = 1
	stats.attack = 2
	stats.defense = 3
	stats.specialAttack = 4
	stats.specialDefense = 5
	stats.speed = 6
	stats.total = 21

	c = Character("Bulbasaur")
	c.setBaseStats(stats)

	assert c.hp == 1
	assert c.attack == 2
	assert c.defense == 3
	assert c.specialAttack == 4
	assert c.specialDefense == 5
	assert c.speed == 6
	assert c.total == 21


def test_character_tab_is_alternate_form():
	tag = makeTag('<a href="#tab-basic">Basic</a>')
	assert CharacterTab(0, tag).isAlternateForm() is False
	assert CharacterTab(1, tag).isAlternateForm() is True


def test_character_tab_reads_name_and_panel():
	tag = makeTag('<a href="#tab-alolan">Alolan Form</a>')
	tab = CharacterTab(1, tag)
	assert tab.name == "Alolan Form"
	assert tab.panel == "#tab-alolan"


def test_dex_moves_tab_reads_name_and_panel_id():
	tag = makeTag('<a href="#tab-moves-8">Generation 8</a>')
	tab = DexMovesTab(tag)
	assert tab.name == "Generation 8"
	assert tab.panelId == "#tab-moves-8"


# --- Dex ---------------------------------------------------------------

def test_dex_to_csv_string():
	d = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
	assert d.toCsvString() == '1,red-blue-yellow,"Red/Blue/Yellow","Red, Blue & Yellow",1\n'


def test_dex_get_url():
	d = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
	assert d.getUrl() == settings.base_dex_url + "game/red-blue-yellow"


def test_dex_model_dump_by_alias_matches_csv_exporter_header():
	d = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
	dumped = d.model_dump(by_alias=True)

	header_columns = csv_exporter.getCsvHeader(Dex).strip().split(",")

	for column in header_columns:
		assert column in dumped

	assert dumped["dex_id"] == 1
	assert dumped["name_id"] == "red-blue-yellow"
	# to_snake would leave "gen" unchanged - it's explicitly aliased to
	# match the header's generation column.
	assert dumped["generation"] == 1


def test_dex_populate_by_name_allows_construction_by_alias():
	d = Dex.model_validate({
		"dex_id": 2,
		"name_id": "gold-silver-crystal",
		"name": "Gold/Silver/Crystal",
		"alternate_name": "",
		"generation": 2,
	})

	assert d.dexId == 2
	assert d.gen == 2


def test_dex_construction_by_keyword_field_name():
	d = Dex(dexId=3, nameId="ruby-sapphire", name="Ruby/Sapphire", alternateName="", gen=3)

	assert d.dexId == 3
	assert d.gen == 3


# --- Dlc ---------------------------------------------------------------

def test_dlc_to_csv_string():
	d = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	assert d.toCsvString() == '1,15,"The Isle of Armor",isle-of-armor\n'


def test_dlc_get_url():
	d = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	assert d.getUrl("sword-shield") == settings.base_dex_url + "game/sword-shield/isle-of-armor"


def test_dlc_model_dump_by_alias_matches_csv_exporter_header():
	d = Dlc(1, 15, "The Isle of Armor", "isle-of-armor")
	dumped = d.model_dump(by_alias=True)

	header_columns = csv_exporter.getCsvHeader(Dlc).strip().split(",")

	for column in header_columns:
		assert column in dumped

	assert dumped["dlc_id"] == 1
	assert dumped["dex_id"] == 15
	assert dumped["name_id"] == "isle-of-armor"


def test_dlc_populate_by_name_allows_construction_by_alias():
	d = Dlc.model_validate({"dlc_id": 2, "dex_id": 15, "name": "The Crown Tundra", "name_id": "crown-tundra"})

	assert d.dlcId == 2
	assert d.dexId == 15


def test_dlc_construction_by_keyword_field_name():
	d = Dlc(dlcId=3, dexId=15, name="The Crown Tundra", nameId="crown-tundra")

	assert d.dlcId == 3
	assert d.name == "The Crown Tundra"


# --- Game ----------------------------------------------------------------

def test_game_to_csv_string_with_single_region():
	g = Game(1, 1, "Red", "red", ["Kanto"])
	assert g.toCsvString() == '1,1,"Red",red,"{Kanto}"\n'


def test_game_to_csv_string_with_multiple_regions():
	g = Game(15, 7, "HeartGold", "heartgold", ["Kanto", "Johto", "Hoenn", "Sinnoh"])
	assert g.toCsvString() == '15,7,"HeartGold",heartgold,"{Kanto,Johto,Hoenn,Sinnoh}"\n'


def test_game_to_csv_string_with_empty_regions():
	g = Game(1, 1, "Red", "red", [])
	assert g.toCsvString() == '1,1,"Red",red,"{}"\n'


def test_game_is_in_dex():
	g = Game(1, 1, "Red", "red", ["Kanto"])
	assert g.isInDex(1) is True
	assert g.isInDex(2) is False


def test_game_model_dump_by_alias_matches_csv_exporter_header():
	g = Game(1, 1, "Red", "red", ["Kanto"])
	dumped = g.model_dump(by_alias=True)

	header_columns = csv_exporter.getCsvHeader(Game).strip().split(",")

	for column in header_columns:
		assert column in dumped

	assert dumped["game_id"] == 1
	assert dumped["dex_id"] == 1
	assert dumped["name_id"] == "red"


def test_game_populate_by_name_allows_construction_by_alias():
	g = Game.model_validate({"game_id": 2, "dex_id": 1, "name": "Blue", "name_id": "blue", "regions": ["Kanto"]})

	assert g.gameId == 2
	assert g.dexId == 1
	assert g.nameId == "blue"


def test_game_construction_by_keyword_field_name():
	g = Game(gameId=3, dexId=1, name="Yellow", nameId="yellow", regions=["Kanto"])

	assert g.gameId == 3
	assert g.name == "Yellow"


# --- Move ------------------------------------------------------------------

def test_move_to_csv_string():
	m = Move("Tackle", "tackle", "Normal", "Physical", "40", "100", "35", "Inflicts regular damage.", "—")
	m.moveId = 1
	assert m.toCsvString() == '1,"Tackle",tackle,Normal,Physical,40,100,35,"Inflicts regular damage.",—\n'


# --- DexCharacter ------------------------------------------------------

def test_dex_character_defaults():
	dc = DexCharacter("bulbasaur", "0001", "thumb.png")
	assert dc.gameId == 0
	assert dc.characterId == 0


def test_dex_character_to_csv_string():
	dc = DexCharacter("bulbasaur", "0001", "thumb.png")
	dc.gameId = 1
	dc.characterId = 5
	assert dc.toCsvString() == '1,5,0001,"thumb.png"\n'


# --- DlcCharacter ------------------------------------------------------

def test_dlc_character_defaults():
	dc = DlcCharacter("bulbasaur", "0001", "thumb.png")
	assert dc.dlcId == 0
	assert dc.characterId == 0


def test_dlc_character_to_csv_string():
	dc = DlcCharacter("bulbasaur", "0001", "thumb.png")
	dc.dlcId = 2
	dc.characterId = 5
	assert dc.toCsvString() == '2,5,0001,"thumb.png"\n'


# --- DexMove -------------------------------------------------------------

def test_dex_move_defaults_before_learned_by_set():
	m = DexMove("Thunderbolt", "thunderbolt", "90", "100")
	assert m.learnedBy == ""
	assert m.learnedById == ""


def test_dex_move_set_learned_by_info():
	m = DexMove("Thunderbolt", "thunderbolt", "90", "100")
	m.setLearnedByInfo("TM", "25")
	assert m.learnedBy == "TM"
	assert m.learnedById == "25"


# --- CharacterDexMove --------------------------------------------------

def test_character_dex_move_converts_dex_name_to_dex_name_id():
	move = DexMove("Tackle", "tackle", "40", "100")
	cdm = CharacterDexMove(5, "Sword/Shield", 8, move)
	assert cdm.dexNameId == "sword-shield"


def test_character_dex_move_copies_fields_from_dex_move():
	move = DexMove("Tackle", "tackle", "40", "100")
	move.setLearnedByInfo("Lv.", "7")

	cdm = CharacterDexMove(5, "Sword/Shield", 8, move)

	assert cdm.characterId == 5
	assert cdm.generation == 8
	assert cdm.moveName == "Tackle"
	assert cdm.moveNameId == "tackle"
	assert cdm.power == "40"
	assert cdm.accuracy == "100"
	assert cdm.learnedBy == "Lv."
	assert cdm.learnedById == "7"


def test_character_dex_move_get_is_suggested():
	move = DexMove("Tackle", "tackle", "40", "100")
	cdm = CharacterDexMove(5, "Sword/Shield", 8, move)
	assert cdm.getIsSuggested() == "f"
	cdm.isSuggested = True
	assert cdm.getIsSuggested() == "t"


def test_character_dex_move_to_csv_string():
	move = DexMove("Tackle", "tackle", "40", "100")
	move.setLearnedByInfo("Lv.", "7")

	cdm = CharacterDexMove(5, "Sword/Shield", 8, move)
	cdm.characterDexMoveId = 1
	cdm.dexId = 15
	cdm.moveId = 33
	cdm.isSuggested = True

	assert cdm.toCsvString() == "1,15,5,33,8,t,40,100,Lv.,7\n"
