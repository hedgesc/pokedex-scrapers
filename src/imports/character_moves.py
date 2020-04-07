import urllib.request
import collections
import re
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras


class CharacterMove:
  def __init__(self):
    self.characterId = 0
    self.generation = 0
    self.moveId = 0
    self.isSuggested = False


def get_moveId(name):
  return name\
    .replace(",", "")\
    .replace("'", "")\
    .replace(" ", "-")\
    .lower()


def get_page(url):
  request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  response = urllib.request.urlopen(request)
  return response.read()


def make_detail_url(pageId):
  return 'https://pokemondb.net/pokedex/' + pageId


def make_detail_moves_by_gen_url(name, gen):
  return make_detail_url(name) + '/moves/{0}'.format(gen)


def character_detail_page(pageId):
  url = make_detail_url(pageId)
  soup = BeautifulSoup(get_page(url), "html.parser")
  return soup


def detail_moves_by_gen_page(name, gen):
  url = make_detail_moves_by_gen_url(name, gen)
  page = BeautifulSoup(get_page(url), "html.parser")
  return page


def text_to_int(text):
  val = text.replace(chr(8212), "").replace(chr(8734), "1000")
    
  if val == "":
      return 0
  else:
      return int(val)


def scrape_moves(page):
  moves = []

  for tab in page.select(".tabs-tab"):
    tables = page.select_one(tab.attrs["href"]).select(".data-table")

    for tbl in tables:
      head1  = tbl.select_one("thead > tr > th > .sortwrap").get_text()

      if head1 in ["Lv.", "HM", "TM"]:

        for row in tbl.select("tbody > tr"):
          columns = row.find_all("td")

          moveId = get_moveId(columns[1].get_text())
          
          if not moveId in moves:
            moves.append(moveId)

  return moves


def get_characters():
  conn = psycopg2.connect("dbname='pokedex' user='postgres' host='localhost' password='Super*32'")
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

  cur.execute("select * from characters order by character_id")
  characters = cur.fetchall()

  conn.close()
  
  return characters


def get_generations():
  return range(1, 9)


def get_moveId_by_nameId(nameId):
  conn = psycopg2.connect("dbname='pokedex' user='postgres' host='localhost' password='Super*32'")
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

  cur.execute("select move_id from moves where name_id = %s", (nameId,))
  moveId = cur.fetchone()

  conn.close()

  if moveId is None:
    return None

  return moveId[0]


def cm_to_csv(cm):
  return "{0},{1},{2}".format(cm.characterId, cm.moveId, cm.generation)


csv = open("character_moves.csv", "w", encoding='utf-8')
csv.truncate(0)

header = "character_id,move_id,generation\n"
csv.write(header)

characters = get_characters()

for c in characters:
  print(c['name'])

  for gen in get_generations():
    print("-- generation {0}".format(gen))

    try:
      page = detail_moves_by_gen_page(c['name_id'], gen)
    except:
      continue

    cmoves = scrape_moves(page)

    for m in cmoves:
      print("---- {0}".format(m))

      cm = CharacterMove()
      cm.characterId = c['character_id']
      cm.generation = gen
      cm.moveId = get_moveId_by_nameId(m)

      if cm.moveId is None:
        print("failed to location move {0}".format(m))
      else:  
        #print("---- " + cm_to_csv(cm))
        csv.write(cm_to_csv(cm) + "\n")

  print()

csv.close()