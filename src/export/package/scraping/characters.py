from copy import copy

from .pages.national import *
from .pages.character import *

def scrapeAllCharacters():
	result = []
	id = 1
	gen = 1
	parser = getNationalDexParser()
	gen_lists = selectGenLists(parser)

	for list in gen_lists:

		print('Scraping generation {0}'.format(gen))
		print()

		cards = selectCharacterCard(list)

		for card in cards:
			base_char = createCharacterFromCard(card)

			if base_char is None:
				continue

			base_char.generation = gen

			print("\t{0} - {1} ...scraping detail".format(base_char.pokemonId, base_char.nameId))

			detail_parser = getCharacterParser(base_char)
			detail_tabs = scrapeDetailForTabs(detail_parser)

			for tab in detail_tabs:
				char = copy(base_char)

				char.characterId = id

				detail_panel = detail_parser.select_one(tab.panel)
				
				if tab.isAlternateForm():
					char.isAlternateForm = True
					char.alternateName = tab.name
					char.imageUrl2 = ''
					
				char.imageUrl1 = scrapeTabForImage(detail_panel)

				stats = scrapeTabForStats(detail_panel)
				char.setBaseStats(stats)

				char.types = scrapeTabForTypes(detail_panel)
				char.abilities = scrapeTabForAbilities(detail_panel)

				if not char.isAlternateForm:
					evolutions = scrapeDetailForEvolutions(detail_parser)

					if len(evolutions) > 0:
						char.finalEvolutionId = evolutions[-1]

					char.imageUrl2 = char.serebiiNetImage()

				result.append(char)

				id += 1

		gen += 1
		print()

	return result

