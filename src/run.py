from pokemondb_net_scrapers.scraping.characters import scrapeAllCharacters
from pokemondb_net_scrapers.scraping.games_characters import scrapeAllDexCharacters
from pokemondb_net_scrapers.scraping.dlcs_characters import scrapeAllDlcCharacters
from pokemondb_net_scrapers.scraping.dexes_characters_moves import scrapeAllCharacterMoves
from pokemondb_net_scrapers.scraping.moves import scrapeAllMoves
from pokemondb_net_scrapers.static.repo import listDexes, listGames, listDlcs
from pokemondb_net_scrapers.services import csv_exporter
from pokemondb_net_scrapers.config import settings


def findDexById(id):
	return next(filter(lambda d: d.dexId == id, dexes), None)


def findDexContainingNameId(nameId):
	return next(filter(lambda d: nameId in d.nameId, dexes), None)


def findCharacterByNameId(nameId):
	return next(filter(lambda c: c.nameId == nameId, characters), None)


def findMoveByNameId(nameId):
	return next(filter(lambda m: m.nameId == nameId, moves), None)


def exportGamesCharacters():
	print("Exporting {0}...".format(settings.games_characters_csv_file))
	
	output_path = settings.csv_output_folder + settings.games_characters_csv_file
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "game_id,character_id,pokemon_id,thumbnail_url\n"

	csv.write(header)

	for g in games:
		dex = findDexById(g.dexId)
		print("\tScraping characters for game {0}".format(g.name))
		dex_characters = scrapeAllDexCharacters(dex)

		for dc in dex_characters:			
			char = findCharacterByNameId(dc.nameId)
			
			dc.gameId = g.gameId
			dc.characterId = char.characterId

			csv.write(dc.toCsvString())
		
		print("\tDone.")
		print()

	print("Done.")
	print()


def exportDlcsCharacters():
	print("Exporting {0}...".format(settings.dlcs_characters_csv_file))
	
	output_path = settings.csv_output_folder + settings.dlcs_characters_csv_file
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "dlc_id,character_id,pokemon_id,thumbnail_url\n"

	csv.write(header)

	for d in dlcs:
		dex = findDexById(d.dexId)

		print("\tScraping characters for dlc {0}".format(d.name))
		
		url = dex.getUrl() + "/" + d.nameId
		dlc_characters = scrapeAllDlcCharacters(url)

		for dc in dlc_characters:			
			char = findCharacterByNameId(dc.nameId)
			
			dc.dlcId = d.dlcId
			dc.characterId = char.characterId

			csv.write(dc.toCsvString())
		
		print("\tDone.")
		print()
	
	print("Done.")
	print()


def exportDexesCharactersMoves():
	print("Exporting {0}...".format(settings.dexes_characters_moves_csv_file))

	output_path = settings.csv_output_folder + settings.dexes_characters_moves_csv_file
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "dex_character_move_id,dex_id,character_id,move_id,generation,is_suggested,power,accuracy,learned_by,learned_by_id\n"

	csv.write(header)

	id = 1

	for c in characters:
		display_name = c.alternateName if c.isAlternateForm else c.name
		print("\tScraping moves for character {0} {1}".format(c.characterId, display_name))

		character_moves = scrapeAllCharacterMoves(c)	

		for cm in character_moves:
			dex = findDexContainingNameId(cm.dexNameId)
			
			if dex is None:
				continue

			cm.dexId = dex.dexId

			move = findMoveByNameId(cm.moveNameId)

			if move is None:
				continue
			
			cm.moveId = move.moveId
			
			cm.characterDexMoveId = id

			csv.write(cm.toCsvString())

			id += 1


	csv.close()

	print("Done.")
	print()


# main
characters = scrapeAllCharacters()
csv_exporter.exportCharacters(characters)

games = listGames()
csv_exporter.exportGames(games)

dexes = listDexes()
exportGamesCharacters()

csv_exporter.exportDexes(dexes)

dlcs = listDlcs()
csv_exporter.exportDlcs(dlcs)

exportDlcsCharacters()

moves = scrapeAllMoves()
csv_exporter.exportMoves(moves)

exportDexesCharactersMoves()
