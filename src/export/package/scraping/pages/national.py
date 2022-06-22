from ...utils import constants
from ...utils import util
from ...utils import web
from ...classes.character import *
from ..shared import infocard

def getNationalDexParser():
	markup = web.getHtml(constants.NATIONAL_DEX_URL)
	return web.getHtmlParser(markup)


def selectGenLists(parser):
	return parser.select('.infocard-list')


def selectCharacterCard(list):
	return list.select('.infocard')


def createCharacterFromCard(card):
	result = Character()

	result.thumbnailUrl = infocard.selectImage(card)
	result.pokemonId = infocard.selectPokemonId(card)
	result.name = infocard.selectName(card)
	result.nameId = util.convertToId(result.name)
	result.types = infocard.selectTypes(card)

	return result