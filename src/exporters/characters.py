import urllib.request
import collections
import re

from bs4 import Tag, NavigableString, BeautifulSoup
from copy import copy
from classes.character import *



def scrape_detail_for_evolutions(detail_page):
  evolutions = []
  evo_list = detail_page.select_one(".infocard-list-evo")
  
  if not evo_list is None:
    cards = evo_list.find_all('div', {'class': ['infocard']})

    for c in cards:
      name = c.select_one('.infocard-lg-data').select_one('a.ent-name').get_text()
      name_id = generate_nameId_from_name(name)
      evolutions.append(name_id)

  return evolutions


def scrape_characters(page):
  csv = open("characters.csv", "w", encoding='utf-8')
  csv.truncate(0)

  header = "character_id,pokemon_id,generation,name,total,hp,attack,defense,\
    special_attack,special_defense,speed,name_id,alternate_name,types,\
      abilities,final_evolution_id,is_visible,thumbnail_url,image_url1,image_url2\n"

  csv.write(header)

  id = 1
  gen = 1
  gens = page.select('.infocard-list')

  for g in gens:
    print('processing generation {0}'.format(gen))
    print()

    cards = g.select('.infocard')

    for c in cards:
      base_char = build_character_from_card(c)

      if base_char is None:
        continue

      base_char.generation = gen

      print("\t{0} - {1} ...scraping detail".format(base_char.pokemonId, base_char.nameId))

      detail_page = get_character_detail_page(base_char.getDetailUrl())
      detail_tabs = scrape_detail_for_tabs(detail_page)

      for tab in detail_tabs:
        char = copy(base_char)
        
        char.characterId = id

        if tab.isAlternateForm():
          char.isAlternateForm = True
          char.alternateName = tab.name
        
        detail_panel = detail_page.select_one(tab.panel)

        char.imageUrl1 = scrape_panel_for_image(detail_panel)

        stats = scrape_panel_for_base_stats(detail_panel)
        char.setBaseStats(stats)

        char.abilities = scrape_panel_for_abilities(detail_panel)

        if not char.isAlternateForm:
          evolutions = scrape_detail_for_evolutions(detail_page)

          if len(evolutions) > 0:
            char.finalEvolutionId = evolutions[-1]

          char.imageUrl2 = char.serebiiNetImage()
        else:
          char.imageUrl2 = ''

        csv.write(character_to_csv(char) + "\n")

        id += 1

    gen = gen + 1
    print()

  csv.close()

scrape_characters(national_page())
print("\nDone.")