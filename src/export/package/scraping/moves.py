from .pages.move.all import *

def scrapeAllMoves():
	print("Scraping all moves...")

	result = []
	parser = getAllMovesParser()
	rows = selectMovesTableRows(parser)
	total = len(rows)
	id = 1
	
	for r in rows:
		print("\tCreating move {0} of {1}".format(id, total))
		move = createMoveFromRow(r)
		move.moveId = id
		result.append(move)
		id += 1

	print("Done.")
	print()

	return result