from ...utils import web
from ...utils import parsing
from ...models.dex_character import DexCharacter
from ..shared import infocard

def getDexParser(dex):
	markup = web.getHtml(dex.getUrl())
	return web.getHtmlParser(markup)


def selectCharacterCards(parser):
	main_list = parser.select_one(".infocard-list")
	return main_list.select(".infocard")


def createDexCharacterFromCard(card):
	thumbnail_url = infocard.selectImage(card)
	pokemon_id = infocard.selectPokemonId(card)
	name_id = parsing.convertToId(infocard.selectName(card))
	result = DexCharacter(name_id, pokemon_id, thumbnail_url)
	return result
	