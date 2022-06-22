from .pages.dlc import *

def scrapeAllDlcCharacters(url):
	result = []
	parser = getDlcParser(url)
	cards = selectCharacterCards(parser)

	for c in cards:
		dex_char = createDlcCharacterFromCard(c)
		result.append(dex_char)

	return result