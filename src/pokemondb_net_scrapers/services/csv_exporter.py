"""Service for exporting model rows (anything with a toCsvString()) to CSV files.

Consumers pass a non-empty list of model instances to export(); the model's
type is used to look up its CSV header and destination filename from the
registries below. Models don't need to know anything about CSV export -
onboarding a new model means adding an entry to each registry.
"""

import os

from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.character import Character
from pokemondb_net_scrapers.models.dex import Dex
from pokemondb_net_scrapers.models.dlc import Dlc
from pokemondb_net_scrapers.models.game import Game
from pokemondb_net_scrapers.models.move import Move

# model class -> CSV header row for that model's export file
csvHeadersByModel = {
	Character: "character_id,pokemon_id,generation,name,total,hp,attack,defense,special_attack,special_defense,speed,name_id,alternate_name,types,abilities,final_evolution_id,is_visible,thumbnail_url,image_url1,image_url2\n",
	Game: "game_id,dex_id,name,name_id,regions\n",
	Dex: "dex_id,name,name_id,alternate_name,generation\n",
	Dlc: "dlc_id,dex_id,name,name_id\n",
	Move: "move_id,name,name_id,type,category,power,accuracy,pp,effect,probability\n",
}

# model class -> settings field name holding that model's output filename
csvFilesByModel = {
	Character: "characters_csv_file",
	Game: "games_csv_file",
	Dex: "dexes_csv_file",
	Dlc: "dlcs_csv_file",
	Move: "moves_csv_file",
}


def getOutputFolder():
	return settings.csv_output_folder


def getCsvHeader(modelClass):
	if modelClass not in csvHeadersByModel:
		raise ValueError("No CSV header registered for {0}".format(modelClass.__name__))

	return csvHeadersByModel[modelClass]


def getOutputPath(modelClass):
	if modelClass not in csvFilesByModel:
		raise ValueError("No output file registered for {0}".format(modelClass.__name__))

	filename = getattr(settings, csvFilesByModel[modelClass])

	return os.path.join(getOutputFolder(), filename)


def export(items):
	items = list(items)

	if not items:
		raise ValueError("export() requires a non-empty list so the model type can be inferred")

	modelClass = type(items[0])
	outputPath = getOutputPath(modelClass)

	os.makedirs(getOutputFolder(), exist_ok=True)

	with open(outputPath, "w", encoding="utf-8") as csv:
		csv.write(getCsvHeader(modelClass))

		for item in items:
			csv.write(item.toCsvString())

	return outputPath


def exportCharacters(characters):
	print("Exporting {0}...".format(settings.characters_csv_file))

	export(characters)

	print("Done.")
	print()


def exportGames(games):
	print("Exporting {0}...".format(settings.games_csv_file))

	export(games)

	print("Done.")
	print()


def exportDexes(dexes):
	print("Exporting {0}...".format(settings.dexes_csv_file))

	export(dexes)

	print("Done.")
	print()


def exportDlcs(dlcs):
	print("Exporting {0}...".format(settings.dlcs_csv_file))

	export(dlcs)

	print("Done.")
	print()


def exportMoves(moves):
	print("Exporting {0}...".format(settings.moves_csv_file))

	export(moves)

	print("Done.")
	print()
