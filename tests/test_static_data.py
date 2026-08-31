import pytest
from pydantic import ValidationError

from pokemondb_net_scrapers.static import repo
from pokemondb_net_scrapers.static.schema import DexList, DlcList, GameList


def test_listDexes_loads_from_yaml():
	dexes = repo.listDexes()
	assert len(dexes) == 16
	assert dexes[0].dexId == 1
	assert dexes[0].nameId == "red-blue-yellow"


def test_listGames_loads_from_yaml():
	games = repo.listGames()
	assert len(games) == 34
	assert games[0].gameId == 1
	assert games[0].regions == ["Kanto"]


def test_listDlcs_loads_from_yaml():
	dlcs = repo.listDlcs()
	assert len(dlcs) == 2
	assert dlcs[0].dlcId == 1


def test_listDexGames_filters_by_dex():
	games = repo.listDexGames(1)
	assert {g.gameId for g in games} == {1, 2, 3}


def test_duplicate_dexId_rejected():
	with pytest.raises(ValidationError, match="Duplicate dex dexId"):
		DexList.model_validate([
			{"dexId": 1, "nameId": "a", "name": "A", "alternateName": "A", "gen": 1},
			{"dexId": 1, "nameId": "b", "name": "B", "alternateName": "B", "gen": 1},
		])


def test_duplicate_game_nameId_rejected():
	with pytest.raises(ValidationError, match="Duplicate game nameId"):
		GameList.model_validate([
			{"gameId": 1, "dexId": 1, "name": "A", "nameId": "dup", "regions": ["Kanto"]},
			{"gameId": 2, "dexId": 1, "name": "B", "nameId": "dup", "regions": ["Kanto"]},
		])


def test_duplicate_dlcId_rejected():
	with pytest.raises(ValidationError, match="Duplicate dlc dlcId"):
		DlcList.model_validate([
			{"dlcId": 1, "dexId": 15, "name": "A", "nameId": "a"},
			{"dlcId": 1, "dexId": 15, "name": "B", "nameId": "b"},
		])
