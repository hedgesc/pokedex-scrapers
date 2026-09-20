from .pages.dex import *

def scrapeAllDexCharacters(dex):
	result = []
	parser = getDexParser(dex)
	cards = selectCharacterCards(parser)

	for c in cards:
		dex_char = createDexCharacterFromCard(c)
		result.append(dex_char)

	return result
