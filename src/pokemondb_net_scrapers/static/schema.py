"""Validation schemas for the hand-maintained reference data in static/data/*.yaml.

These mirror the constructor fields of models.dex.Dex, models.game.Game, and
models.dlc.Dlc, plus duplicate-id/duplicate-nameId checks that a plain YAML file
can't enforce on its own. See static/data.py for where these are loaded and used.
"""

from collections import Counter

from pydantic import BaseModel, RootModel, model_validator


def _requireUnique(rootModel, field, label):
	counts = Counter(getattr(entry, field) for entry in rootModel.root)
	duplicates = sorted(value for value, count in counts.items() if count > 1)
	if duplicates:
		raise ValueError(f"Duplicate {label} {field}: {duplicates}")
	return rootModel


class DexEntry(BaseModel):
	dexId: int
	nameId: str
	name: str
	alternateName: str
	gen: int


class DexList(RootModel[list[DexEntry]]):
	@model_validator(mode="after")
	def checkUnique(self):
		_requireUnique(self, "dexId", "dex")
		_requireUnique(self, "nameId", "dex")
		return self


class GameEntry(BaseModel):
	gameId: int
	dexId: int
	name: str
	nameId: str
	regions: list[str]


class GameList(RootModel[list[GameEntry]]):
	@model_validator(mode="after")
	def checkUnique(self):
		_requireUnique(self, "gameId", "game")
		_requireUnique(self, "nameId", "game")
		return self


class DlcEntry(BaseModel):
	dlcId: int
	dexId: int
	name: str
	nameId: str


class DlcList(RootModel[list[DlcEntry]]):
	@model_validator(mode="after")
	def checkUnique(self):
		_requireUnique(self, "dlcId", "dlc")
		return self
