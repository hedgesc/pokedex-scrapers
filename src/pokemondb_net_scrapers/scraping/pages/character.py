from pokemondb_net_scrapers.classes.dex_move import DexMove
from pokemondb_net_scrapers.config import settings
from ...utils import web
from ...utils import util
from ...classes.character import *


def getCharacterParser(c):
	markup = web.getHtml(c.getDetailUrl())
	return web.getHtmlParser(markup)


def getCharacterMovesParser(c, gen):
  url = c.getDetailUrl() + "/moves/{0}".format(gen)
  markup = web.getHtml(url)
  return web.getHtmlParser(markup)


def scrapeDetailForTabs(detail_parser):
  result = []
  tabs = detail_parser.select(".tabset-basics > .sv-tabs-tab-list > .sv-tabs-tab")

  i = 0
  for t in tabs:
    char_tab = CharacterTab(i, t)
    result.append(char_tab)
    i += 1

  return result


def scrapeDetailForEvolutions(detail_page):
  evolutions = []
  evo_list = detail_page.select_one(".infocard-list-evo")
  
  if not evo_list is None:
    cards = evo_list.find_all('div', {'class': ['infocard']})

    for c in cards:
      name = c.select_one('.infocard-lg-data').select_one('a.ent-name').get_text()
      name_id = util.convertToId(name)
      evolutions.append(name_id)

  return evolutions


def scrapeTabForImage(detail_panel):
  img_tag = detail_panel.select_one(".grid-row").select_one(".grid-col").select_one("img")
  return img_tag['src']


def scrapeTabForTypes(detail_panel):
  result = []
  row = findVitalsTableRow(detail_panel, "Pokédex data", "Type")

  if row is None:
    return result

  anchors = row.select("td > a")

  for a in anchors:
    result.append(a.get_text())

  return result


def scrapeTabForStats(detail_panel):
  stats = BaseStats()
  rows = detail_panel.select('#dex-stats ~ .resp-scroll > .vitals-table tr')

  for r in rows:
    h = r.select_one('th').get_text()
    n = r.select('td')[0].get_text()

    if(h == 'HP'):
      stats.hp = int(n)
    elif(h == 'Attack'):
      stats.attack = int(n)
    elif(h == 'Defense'):
      stats.defense = int(n)
    elif(h == 'Sp. Atk'):
      stats.specialAttack = int(n)
    elif(h == 'Sp. Def'):
      stats.specialDefense = int(n)
    elif(h == 'Speed'):
      stats.speed = int(n)
    elif(h == 'Total'):
      stats.total = int(n)

  return stats


def findVitalsTable(panel, table_name):
  table = None
  
  cols = panel.select(".grid-col")
  
  for c in cols:
    h_tag = c.select_one("h2")
    
    if h_tag is None:
      continue

    if h_tag.get_text() == table_name:
      table = c.select_one(".vitals-table")
      break

  return table


def findVitalsTableRow(panel, table_name, row_title):
  table = findVitalsTable(panel, table_name)

  if table is None:
    return None

  result = None

  rows = table.select("tr")

  for r in rows:
    h_tag = r.select_one("th")

    if h_tag is None:
      continue

    if h_tag.get_text() == row_title:
      result = r
      break

  return result

      
def scrapeTabForAbilities(detail_panel):
  result = []
  row = findVitalsTableRow(detail_panel, "Pokédex data", "Abilities")

  if row is None:
    return result

  anchors = row.select("td > span > a")

  for a in anchors:
    result.append(a.get_text())

  return result



def findNavListByTitle(parser, title):
  result = None
  nav_lists = parser.select(".list-nav")
  
  for list in nav_lists:
    list_title = list.select_one(".list-nav-title")

    if list_title is None:
      continue
    
    if list_title.get_text() == title:
      result = list
      break

  return result


def scrapeMoveGenerations(parser):
  result = []
  nav_list = findNavListByTitle(parser, "In other generations")

  if nav_list is None:
    result.append(settings.current_gen)
  else:
    items = nav_list.select("li")
    
    for item in items:
      gen_link = item.select_one("a")
      
      if not gen_link is None:
        gen_text = gen_link.get_text()
        result.append(int(gen_text))

  return result


def scrapeMovesTabs(parser):
  result = []
  tabs = parser.select(".tabset-moves-game > .sv-tabs-tab-list > .sv-tabs-tab")

  for t in tabs:
    moves_tab = DexMovesTab(t)
    result.append(moves_tab)

  return result


def scrapePanelForMoves(panel):
  moves = []

  panel_tables = panel.select(".grid-col > .resp-scroll > .data-table")

  for tbl in panel_tables:
    head1  = tbl.select_one("thead > tr > th > .sortwrap").get_text()
    if head1 in ["Lv.", "HM", "TM"]:
      
      for row in tbl.select("tbody > tr"):
        columns = row.find_all("td")
        
        id = columns[0].get_text()

        move_link = columns[1].find("a")
        move_name = move_link.get_text()
        move_name_id = move_link["href"].split("/")[-1]

        power = columns[4].get_text()
        accuracy = columns[5].get_text()

        move = DexMove(move_name, move_name_id, power, accuracy)
        move.setLearnedByInfo(head1, id)

        moves.append(move)

  moves.sort(key = lambda m: (m.power, m.learnedById), reverse = True)

  return moves
