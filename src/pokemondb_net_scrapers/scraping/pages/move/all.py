from ....utils import web
from ....config import settings
from ....utils import util
from ....classes.move import Move

def getAllMovesParser():
	markup = web.getHtml(settings.all_moves_url)
	return web.getHtmlParser(markup)


def selectMovesTableRows(parser):
	return parser.select("#moves > tbody > tr")


def createMoveFromRow(row):
	cols = row.find_all("td")

	name = cols[0].select_one("a").get_text()
	nameId = util.convertToId(name)
	
	typeAnchor = cols[1].select_one("a")
	type = "" if typeAnchor is None else typeAnchor.get_text()
	
	categoryImg = cols[2].select_one("img")
	category = "" if categoryImg is None else categoryImg.attrs["title"]

	power = cols[3].get_text()
	accuracy = cols[4].get_text()
	pp = cols[5].get_text()
	effect = cols[7].get_text()
	probability = cols[8].get_text()
	
	result = Move(name, nameId, type, category, power, accuracy, pp, effect, probability)
	return result