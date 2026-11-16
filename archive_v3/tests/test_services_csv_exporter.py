import os

import pytest

from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.character import Character
from pokemondb_net_scrapers.models.dex import Dex
from pokemondb_net_scrapers.models.dlc import Dlc
from pokemondb_net_scrapers.models.dlc_character import DlcCharacter
from pokemondb_net_scrapers.models.game import Game
from pokemondb_net_scrapers.models.game_character import GameCharacter
from pokemondb_net_scrapers.models.move import Move
from pokemondb_net_scrapers.services import csv_exporter


def makeCharacter(characterId, name):
	c = Character(name)
	c.characterId = characterId
	c.pokemonId = "000{0}".format(characterId)
	c.generation = 1
	c.types = ["Grass"]
	c.abilities = ["Overgrow"]

	return c


def makeGame(gameId, name):
	return Game(gameId, 1, name, name.lower(), ["Kanto"])


def makeDex(dexId, name):
	return Dex(dexId, name.lower(), name, "", 1)


def makeDlc(dlcId, name):
	return Dlc(dlcId, 1, name, name.lower())


def makeMove(moveId, name):
	m = Move(name, name.lower(), "Normal", "Physical", "40", "100", "35", "", "")
	m.moveId = moveId

	return m


def makeGameCharacter(gameId, characterId, pokemonId):
	gc = GameCharacter("pikachu", pokemonId, "thumb.png")
	gc.gameId = gameId
	gc.characterId = characterId

	return gc


def makeDlcCharacter(dlcId, characterId, pokemonId):
	dc = DlcCharacter("kubfu", pokemonId, "thumb.png")
	dc.dlcId = dlcId
	dc.characterId = characterId

	return dc


def test_get_output_folder_returns_configured_folder():
	assert csv_exporter.getOutputFolder() == settings.csv_output_folder


@pytest.mark.parametrize("modelClass,expectedPrefix", [
	(Character, "character_id,pokemon_id,"),
	(Game, "game_id,dex_id,"),
	(GameCharacter, "game_id,character_id,"),
	(Dex, "dex_id,name,"),
	(Dlc, "dlc_id,dex_id,"),
	(DlcCharacter, "dlc_id,character_id,"),
	(Move, "move_id,name,"),
])
def test_get_csv_header_returns_registered_header(modelClass, expectedPrefix):
	header = csv_exporter.getCsvHeader(modelClass)

	assert header.startswith(expectedPrefix)
	assert header.endswith("\n")


def test_get_csv_header_raises_for_unregistered_model():
	class NotRegistered:
		pass

	with pytest.raises(ValueError):
		csv_exporter.getCsvHeader(NotRegistered)


@pytest.mark.parametrize("modelClass,settingsField", [
	(Character, "characters_csv_file"),
	(Game, "games_csv_file"),
	(GameCharacter, "games_characters_csv_file"),
	(Dex, "dexes_csv_file"),
	(Dlc, "dlcs_csv_file"),
	(DlcCharacter, "dlcs_characters_csv_file"),
	(Move, "moves_csv_file"),
])
def test_get_output_path_uses_settings_filename(monkeypatch, tmp_path, modelClass, settingsField):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, settingsField, "output.csv")

	path = csv_exporter.getOutputPath(modelClass)

	assert path == os.path.join(str(tmp_path), "output.csv")


def test_get_output_path_raises_for_unregistered_model():
	class NotRegistered:
		pass

	with pytest.raises(ValueError):
		csv_exporter.getOutputPath(NotRegistered)


def test_export_writes_header_and_rows(monkeypatch, tmp_path):
	output_folder = tmp_path / "nested"
	monkeypatch.setattr(settings, "csv_output_folder", str(output_folder))
	monkeypatch.setattr(settings, "characters_csv_file", "characters.csv")

	characters = [makeCharacter(1, "Bulbasaur"), makeCharacter(2, "Ivysaur")]

	output_path = csv_exporter.export(characters)

	assert output_path == os.path.join(str(output_folder), "characters.csv")

	with open(output_path, encoding="utf-8") as f:
		lines = f.readlines()

	assert lines[0] == csv_exporter.getCsvHeader(Character)
	assert len(lines) == 3
	assert "Bulbasaur" in lines[1]
	assert "Ivysaur" in lines[2]


def test_export_creates_output_folder_if_missing(monkeypatch, tmp_path):
	output_folder = tmp_path / "does_not_exist_yet"
	monkeypatch.setattr(settings, "csv_output_folder", str(output_folder))
	monkeypatch.setattr(settings, "characters_csv_file", "characters.csv")

	assert not output_folder.exists()

	csv_exporter.export([makeCharacter(1, "Bulbasaur")])

	assert output_folder.exists()


def test_export_overwrites_existing_file(monkeypatch, tmp_path):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, "characters_csv_file", "characters.csv")

	csv_exporter.export([makeCharacter(1, "Bulbasaur"), makeCharacter(2, "Ivysaur")])
	csv_exporter.export([makeCharacter(3, "Venusaur")])

	with open(os.path.join(str(tmp_path), "characters.csv"), encoding="utf-8") as f:
		lines = f.readlines()

	assert len(lines) == 2
	assert "Venusaur" in lines[1]


def test_export_raises_on_empty_list():
	with pytest.raises(ValueError):
		csv_exporter.export([])


def test_export_writes_game_characters(monkeypatch, tmp_path):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, "games_characters_csv_file", "games_characters.csv")

	rows = [makeGameCharacter(1, 25, "0025"), makeGameCharacter(1, 26, "0026")]

	output_path = csv_exporter.export(rows)

	with open(output_path, encoding="utf-8") as f:
		lines = f.readlines()

	assert lines[0] == csv_exporter.getCsvHeader(GameCharacter)
	assert len(lines) == 3
	assert "0025" in lines[1]


def test_export_writes_dlc_characters(monkeypatch, tmp_path):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, "dlcs_characters_csv_file", "dlcs_characters.csv")

	rows = [makeDlcCharacter(1, 891, "0891"), makeDlcCharacter(1, 892, "0892")]

	output_path = csv_exporter.export(rows)

	with open(output_path, encoding="utf-8") as f:
		lines = f.readlines()

	assert lines[0] == csv_exporter.getCsvHeader(DlcCharacter)
	assert len(lines) == 3
	assert "0891" in lines[1]


def test_export_characters_writes_header_and_rows(monkeypatch, tmp_path, capsys):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, "characters_csv_file", "characters.csv")

	characters = [makeCharacter(1, "Bulbasaur"), makeCharacter(2, "Ivysaur")]

	csv_exporter.exportCharacters(characters)

	with open(os.path.join(str(tmp_path), "characters.csv"), encoding="utf-8") as f:
		lines = f.readlines()

	assert lines[0] == csv_exporter.getCsvHeader(Character)
	assert len(lines) == 3

	output = capsys.readouterr().out
	assert "Exporting characters.csv..." in output
	assert "Done." in output


def test_export_games_writes_header_and_rows(monkeypatch, tmp_path, capsys):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, "games_csv_file", "games.csv")

	games = [makeGame(1, "Red"), makeGame(2, "Blue")]

	csv_exporter.exportGames(games)

	with open(os.path.join(str(tmp_path), "games.csv"), encoding="utf-8") as f:
		lines = f.readlines()

	assert lines[0] == csv_exporter.getCsvHeader(Game)
	assert len(lines) == 3

	output = capsys.readouterr().out
	assert "Exporting games.csv..." in output
	assert "Done." in output


def test_export_dexes_writes_header_and_rows(monkeypatch, tmp_path, capsys):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, "dexes_csv_file", "dexes.csv")

	dexes = [makeDex(1, "Kanto"), makeDex(2, "Johto")]

	csv_exporter.exportDexes(dexes)

	with open(os.path.join(str(tmp_path), "dexes.csv"), encoding="utf-8") as f:
		lines = f.readlines()

	assert lines[0] == csv_exporter.getCsvHeader(Dex)
	assert len(lines) == 3

	output = capsys.readouterr().out
	assert "Exporting dexes.csv..." in output
	assert "Done." in output


def test_export_dlcs_writes_header_and_rows(monkeypatch, tmp_path, capsys):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, "dlcs_csv_file", "dlcs.csv")

	dlcs = [makeDlc(1, "Isle of Armor"), makeDlc(2, "Crown Tundra")]

	csv_exporter.exportDlcs(dlcs)

	with open(os.path.join(str(tmp_path), "dlcs.csv"), encoding="utf-8") as f:
		lines = f.readlines()

	assert lines[0] == csv_exporter.getCsvHeader(Dlc)
	assert len(lines) == 3

	output = capsys.readouterr().out
	assert "Exporting dlcs.csv..." in output
	assert "Done." in output


def test_export_moves_writes_header_and_rows(monkeypatch, tmp_path, capsys):
	monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
	monkeypatch.setattr(settings, "moves_csv_file", "moves.csv")

	moves = [makeMove(1, "Tackle"), makeMove(2, "Growl")]

	csv_exporter.exportMoves(moves)

	with open(os.path.join(str(tmp_path), "moves.csv"), encoding="utf-8") as f:
		lines = f.readlines()

	assert lines[0] == csv_exporter.getCsvHeader(Move)
	assert len(lines) == 3

	output = capsys.readouterr().out
	assert "Exporting moves.csv..." in output
	assert "Done." in output
