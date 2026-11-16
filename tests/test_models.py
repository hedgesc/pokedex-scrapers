from bs4 import BeautifulSoup

from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.character import BaseStats, Character, CharacterTab, DexMovesTab
from pokemondb_net_scrapers.models.character_seed import CharacterSeed
from pokemondb_net_scrapers.models.dex import Dex
from pokemondb_net_scrapers.models.dex_character import DexCharacter, GameCharacter
from pokemondb_net_scrapers.models.game_character_move import GameCharacterMove
from pokemondb_net_scrapers.models.game_move import GameMove
from pokemondb_net_scrapers.models.move import Move


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


def test_dex_model_dump_by_alias_uses_generation_column():
	d = Dex(1, "red-blue-yellow", "Red/Blue/Yellow", "Red, Blue & Yellow", 1)
	dumped = d.model_dump(by_alias=True)

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


# --- GameCharacter -------------------------------------------------------

def test_game_character_defaults():
	gc = GameCharacter("bulbasaur", "0001", "thumb.png")
	assert gc.gameId == 0
	assert gc.characterId == 0


def test_game_character_to_csv_string():
	gc = GameCharacter("bulbasaur", "0001", "thumb.png")
	gc.gameId = 1
	gc.characterId = 5
	assert gc.toCsvString() == '1,5,0001,"thumb.png"\n'


def test_game_character_model_dump_by_alias_uses_snake_case():
	gc = GameCharacter("bulbasaur", "0001", "thumb.png")
	gc.gameId = 1
	gc.characterId = 5
	dumped = gc.model_dump(by_alias=True)

	assert dumped["game_id"] == 1
	assert dumped["character_id"] == 5
	assert dumped["pokemon_id"] == "0001"
	assert dumped["thumbnail_url"] == "thumb.png"
	assert dumped["name_id"] == "bulbasaur"


def test_game_character_populate_by_name_allows_construction_by_alias():
	gc = GameCharacter.model_validate({
		"name_id": "bulbasaur",
		"pokemon_id": "0001",
		"thumbnail_url": "thumb.png",
		"game_id": 1,
		"character_id": 5,
	})

	assert gc.nameId == "bulbasaur"
	assert gc.gameId == 1
	assert gc.characterId == 5


# --- Move ------------------------------------------------------------------

def test_move_to_csv_string():
	m = Move("Tackle", "tackle", "Normal", "Physical", "40", "100", "35", "Inflicts regular damage.", "—")
	m.moveId = 1
	assert m.toCsvString() == '1,"Tackle",tackle,Normal,Physical,40,100,35,"Inflicts regular damage.",—\n'


def test_move_defaults_before_move_id_set():
	m = Move("Tackle", "tackle", "Normal", "Physical", "40", "100", "35", "Inflicts regular damage.", "—")
	assert m.moveId == 0


def test_move_model_dump_by_alias_uses_snake_case():
	m = Move("Tackle", "tackle", "Normal", "Physical", "40", "100", "35", "Inflicts regular damage.", "—")
	m.moveId = 1
	dumped = m.model_dump(by_alias=True)

	assert dumped["move_id"] == 1
	assert dumped["name"] == "Tackle"
	assert dumped["name_id"] == "tackle"
	assert dumped["type"] == "Normal"
	assert dumped["category"] == "Physical"
	assert dumped["pp"] == "35"


def test_move_populate_by_name_allows_construction_by_alias():
	m = Move.model_validate({
		"name": "Tackle",
		"name_id": "tackle",
		"type": "Normal",
		"category": "Physical",
		"power": "40",
		"accuracy": "100",
		"pp": "35",
		"effect": "Inflicts regular damage.",
		"probability": "—",
		"move_id": 1,
	})

	assert m.nameId == "tackle"
	assert m.moveId == 1


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


# --- GameMove -------------------------------------------------------------

def test_game_move_defaults_before_learned_by_set():
	m = GameMove("Thunderbolt", "thunderbolt", "90", "100")
	assert m.learnedBy == ""
	assert m.learnedById == ""


def test_game_move_set_learned_by_info():
	m = GameMove("Thunderbolt", "thunderbolt", "90", "100")
	m.setLearnedByInfo("TM", "25")
	assert m.learnedBy == "TM"
	assert m.learnedById == "25"


# --- GameCharacterMove --------------------------------------------------

def test_game_character_move_converts_dex_name_to_dex_name_id():
	move = GameMove("Tackle", "tackle", "40", "100")
	row = GameCharacterMove(5, "Sword/Shield", 8, move)
	assert row.dexNameId == "sword-shield"


def test_game_character_move_copies_fields_from_game_move():
	move = GameMove("Tackle", "tackle", "40", "100")
	move.setLearnedByInfo("Lv.", "7")

	row = GameCharacterMove(5, "Sword/Shield", 8, move)

	assert row.characterId == 5
	assert row.generation == 8
	assert row.moveName == "Tackle"
	assert row.moveNameId == "tackle"
	assert row.power == "40"
	assert row.accuracy == "100"
	assert row.learnedBy == "Lv."
	assert row.learnedById == "7"


def test_game_character_move_get_is_suggested():
	move = GameMove("Tackle", "tackle", "40", "100")
	row = GameCharacterMove(5, "Sword/Shield", 8, move)
	assert row.getIsSuggested() == "f"
	row.isSuggested = True
	assert row.getIsSuggested() == "t"


def test_game_character_move_to_csv_string():
	move = GameMove("Tackle", "tackle", "40", "100")
	move.setLearnedByInfo("Lv.", "7")

	row = GameCharacterMove(5, "Sword/Shield", 8, move)
	row.gameCharacterMoveId = 1
	row.dexId = 15
	row.moveId = 33
	row.isSuggested = True

	assert row.toCsvString() == "1,15,5,33,8,t,40,100,Lv.,7\n"


def test_character_seed_derives_name_id():
	seed = CharacterSeed("Mr. Mime")
	assert seed.nameId == "mr-mime"
	assert seed.characterId == 0
