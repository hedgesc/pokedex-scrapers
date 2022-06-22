from package.scraping.characters import scrapeAllCharacters
from package.scraping.games_characters import scrapeAllDexCharacters
from package.scraping.dlcs_characters import scrapeAllDlcCharacters
from package.scraping.dexes_characters_moves import scrapeAllCharacterMoves
from package.scraping.moves import scrapeAllMoves
from package.static.repo import listDexes, listGames, listDlcs
from package.utils import constants


def findDexById(id):
	return next(filter(lambda d: d.dexId == id, dexes), None)


def findDexContainingNameId(nameId):
	return next(filter(lambda d: nameId in d.nameId, dexes), None)


def findCharacterByNameId(nameId):
	return next(filter(lambda c: c.nameId == nameId, characters), None)


def findMoveByNameId(nameId):
	return next(filter(lambda m: m.nameId == nameId, moves), None)


def exportCharacters():
	print("Exporting {0}...".format(constants.CHARACTERS_CSV_FILE))
	
	output_path = constants.CSV_OUTPUT_FOLDER + constants.CHARACTERS_CSV_FILE
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "character_id,pokemon_id,generation,name,total,hp,attack,defense,\
		special_attack,special_defense,speed,name_id,alternate_name,types,\
			abilities,final_evolution_id,is_visible,thumbnail_url,image_url1,image_url2\n"

	csv.write(header)

	for c in characters:
		csv.write(c.toCsvString())

	csv.close()

	print("Done.")
	print()


def exportGames():
	print("Exporting {0}...".format(constants.GAMES_CSV_FILE))
	
	output_path = constants.CSV_OUTPUT_FOLDER + constants.GAMES_CSV_FILE
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "game_id,dex_id,name,name_id,regions\n"

	csv.write(header)

	for g in games:
		csv.write(g.toCsvString())

	csv.close()

	print("Done.")
	print()


def exportGamesCharacters():
	print("Exporting {0}...".format(constants.GAMES_CHARACTERS_CSV_FILE))
	
	output_path = constants.CSV_OUTPUT_FOLDER + constants.GAMES_CHARACTERS_CSV_FILE
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


def exportDexes():
	print("Exporting {0}...".format(constants.DEXES_CSV_FILE))
	
	output_path = constants.CSV_OUTPUT_FOLDER + constants.DEXES_CSV_FILE
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "dex_id,name,name_id,alternate_name,generation\n"

	csv.write(header)

	for d in dexes:
		csv.write(d.toCsvString())

	csv.close()

	print("Done.")
	print()


def exportDlcs():
	print("Exporting {0}...".format(constants.DLCS_CSV_FILE))
	
	output_path = constants.CSV_OUTPUT_FOLDER + constants.DLCS_CSV_FILE
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "dlc_id,dex_id,name,name_id\n"

	csv.write(header)

	for d in dlcs:
		csv.write(d.toCsvString())

	csv.close()

	print("Done.")
	print()


def exportDlcsCharacters():
	print("Exporting {0}...".format(constants.DLCS_CHARACTERS_CSV_FILE))
	
	output_path = constants.CSV_OUTPUT_FOLDER + constants.DLCS_CHARACTERS_CSV_FILE
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


def exportMoves():
	print("Exporting {0}...".format(constants.MOVES_CSV_FILE))
	
	output_path = constants.CSV_OUTPUT_FOLDER + constants.MOVES_CSV_FILE
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "move_id,name,name_id,type,category,power,accuracy,pp,effect,probability\n"

	csv.write(header)

	for m in moves:
		csv.write(m.toCsvString())

	csv.close()

	print("Done.")
	print()


def exportDexesCharactersMoves():
	print("Exporting {0}...".format(constants.DEXES_CHARACTERS_MOVES_CSV_FILE))

	output_path = constants.CSV_OUTPUT_FOLDER + constants.DEXES_CHARACTERS_MOVES_CSV_FILE
	csv = open(output_path, "w", encoding="utf-8")
	csv.truncate(0)

	header = "dex_id,character_id,move_id,generation,is_suggested,power,accuracy,learned_by,learned_by_id\n"

	csv.write(header)

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

			csv.write(cm.toCsvString())


	csv.close()

	print("Done.")
	print()


# main
characters = scrapeAllCharacters()
exportCharacters()

games = listGames()
exportGames()

dexes = listDexes()

exportGamesCharacters()

exportDexes()

dlcs = listDlcs()
exportDlcs()

exportDlcsCharacters()

moves = scrapeAllMoves()
exportMoves()

exportDexesCharactersMoves()
