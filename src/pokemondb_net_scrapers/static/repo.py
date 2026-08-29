from .data import dexes, games, dlcs

def listDexes():
	return dexes

def listGames():
	return games

def listDlcs():
	return dlcs

def listDexGames(dexId):
	return [g for g in games if g.isInDex(dexId)]
	