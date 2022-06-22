from ...utils import web
from ...utils import util
from ...classes.dex_character import DexCharacter
from ..shared import infocard

def getDexParser(dex):
	markup = web.getHtml(dex.getUrl())
	return web.getHtmlParser(markup)


def selectCharacterCards(parser):
	return parser.select('.infocard-list > .infocard')


def createDexCharacterFromCard(card):
	thumbnail_url = infocard.selectImage(card)
	pokemon_id = infocard.selectPokemonId(card)
	name_id = util.convertToId(infocard.selectName(card))
	result = DexCharacter(name_id, pokemon_id, thumbnail_url)
	return result
	