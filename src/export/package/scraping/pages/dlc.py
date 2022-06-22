from ...utils import web
from ...utils import util
from ...classes.dlc_character import DlcCharacter
from ..shared import infocard

def getDlcParser(url):
	markup = web.getHtml(url)
	return web.getHtmlParser(markup)


def selectCharacterCards(parser):
	return parser.select('.infocard-list > .infocard')


def createDlcCharacterFromCard(card):
	thumbnail_url = infocard.selectImage(card)
	pokemon_id = infocard.selectPokemonId(card)
	name_id = util.convertToId(infocard.selectName(card))
	result = DlcCharacter(name_id, pokemon_id, thumbnail_url)
	return result
	