"""Loads the hand-maintained dex/game/DLC reference data from static/data/*.yaml.

pokemondb.net doesn't expose a clean enumerable list of its games/dexes/DLCs, so
this data isn't scraped -- it's hand-maintained in the YAML files under
static/data/ and those files must be updated by hand when new games/dexes/DLCs
are added. See schema.py for the validation (duplicate ids/nameIds) applied
while loading.
"""

from pathlib import Path

import yaml

from ..models.dex import Dex
from ..models.dlc import Dlc
from ..models.game import Game
from .schema import DexList, DlcList, GameList

_dataDir = Path(__file__).parent / "data"


def _loadYaml(fileName):
	with open(_dataDir / fileName, "r", encoding="utf-8") as f:
		return yaml.safe_load(f)


_dexEntries = DexList.model_validate(_loadYaml("dexes.yaml")).root
_gameEntries = GameList.model_validate(_loadYaml("games.yaml")).root
_dlcEntries = DlcList.model_validate(_loadYaml("dlcs.yaml")).root

_knownDexIds = {entry.dexId for entry in _dexEntries}

for _entry in _gameEntries:
	if _entry.dexId not in _knownDexIds:
		raise ValueError(f"games.yaml: game '{_entry.name}' references unknown dexId {_entry.dexId}")

for _entry in _dlcEntries:
	if _entry.dexId not in _knownDexIds:
		raise ValueError(f"dlcs.yaml: dlc '{_entry.name}' references unknown dexId {_entry.dexId}")

dexes = [Dex(e.dexId, e.nameId, e.name, e.alternateName, e.gen) for e in _dexEntries]

games = [Game(e.gameId, e.dexId, e.name, e.nameId, e.regions) for e in _gameEntries]

dlcs = [Dlc(e.dlcId, e.dexId, e.name, e.nameId) for e in _dlcEntries]
