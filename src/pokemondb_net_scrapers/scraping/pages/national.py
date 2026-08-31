from ...config import settings
from ...utils import parsing
from ...utils import web
from ...models.character import *
from ..shared import infocard

def getNationalDexParser():
	markup = web.getHtml(settings.national_dex_url)
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
	result.nameId = parsing.convertToId(result.name)
	result.types = infocard.selectTypes(card)

	return result