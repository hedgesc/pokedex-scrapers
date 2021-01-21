import collections
import psycopg2
import psycopg2.extras
import urllib.request
from bs4 import BeautifulSoup


connection_string = "dbname='pokemondb' user='postgres' host='localhost' password='Super*32'"
# pi-zero
# connection_string  = "dbname='pokemondb' user='pi' host='10.0.0.42' password='Super*32'"


def get_dexId_by_nameId(name_id):
  sql = """ select dex_id from dexes where name_id = %s """
  
  conn = None
  dex_id = None

  try:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql, (name_id,))
    dex_id = cur.fetchone()[0]
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
    return dex_id


def insert_dex_character_move(dex_character_move):
  sql = """ 
    INSERT INTO dex_character_moves
    (
      dex_id, character_id, move_id, is_suggested
    )
    VALUES
    (
      %(dex_id)s, %(character_id)s, %(move_id)s, %(is_suggested)s
    ) 
    ON CONFLICT (dex_id, character_id, move_id) 
    DO NOTHING;
  """
  
  conn = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, dex_character_move)
    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()


def get_move_nameId(name):
  return name\
    .replace(",", "")\
    .replace("'", "")\
    .replace(" ", "-")\
    .lower()


def get_move_id_by_name_id(name_id):
  return all_moves[name_id]


def get_all_moves():
  sql = """ select move_id, name_id from moves """

  moves = []
  conn = None

  try:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    moves = cur.fetchall()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
    return moves


def load_moves():
  moves = get_all_moves()
  for m in moves:
    all_moves[m["name_id"]] = m["move_id"]
    

def print_counter(i, tot):
  #print "{:.0%}".format(1/3)
  print("{0}/{1} {2:.0%}".format(i, tot, i/tot))
  print()


def get_page(url):
  request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  response = urllib.request.urlopen(request)
  return response.read()


def build_scraper(url):
  return BeautifulSoup(get_page(url), "html.parser")


def get_all_characters():
  sql = """ select character_id, pokemon_id, name, name_id, gen
    from characters order by character_id """

  conn = None
  characters = []

  try:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    characters = cur.fetchall()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
    return characters


def get_dex_nameId(name):
  name = name.replace("'", "")

  letsgo = "Lets Go "
  two = " 2"

  if two in name:
    name = name.replace(two, "")
    name = name + two

  if letsgo in name:
    name = name.replace(letsgo, "")
    name = "lets-go-" + name

  return name\
    .replace(" ", "-")\
    .replace("/", "-")\
    .lower()


def text_to_int(text):
  val = text.replace(chr(8212), "").replace(chr(8734), "1000")
    
  if val == "":
    return 0
  else:
    return int(val)


def scrape_dex_moves(scraper, moves_panel_id):
  moves = []

  panel = scraper.select_one(moves_panel_id)
  tables = panel.select(".data-table")
  
  for tbl in tables:
    head1  = tbl.select_one("thead > tr > th > .sortwrap").get_text()
    if head1 in ["Lv.", "HM", "TM"]:
      for row in tbl.select("tbody > tr"):
        columns = row.find_all("td")
        move_name_id = get_move_nameId(columns[1].get_text())
        power = text_to_int(columns[4].get_text())
        move_info = { 
          "name_id": move_name_id, 
          "power": power 
        }
        moves.append(move_info)

  moves.sort(key = lambda m: m["power"], reverse = True)
  return moves


def scrape_pokemon_dexes(character, gen):
  character_id = character["character_id"]

  url = "https://pokemondb.net/pokedex/{0}/moves/{1}"\
      .format(character["name_id"], gen)
    
  scraper = build_scraper(url)

  tabset = scraper.select_one(".tabs-tab-list")
  tabs = tabset.select(".tabs-tab")

  for tab in tabs:
    dex_name_id = get_dex_nameId(tab.get_text())
    dex_id = get_dexId_by_nameId(dex_name_id)
    
    if dex_id is None:
      continue

    print("---- {0} ({1})".format(dex_name_id, dex_id))

    moves_panel_id = tab["href"]
    moves = scrape_dex_moves(scraper, moves_panel_id)
    
    i = 0

    for m in moves:
      move_id = get_move_id_by_name_id(m["name_id"])

      if move_id is None:
        continue

      i += 1
      dcm = {
        "character_id": character_id,
        "dex_id": dex_id,
        "move_id": move_id,
        "is_suggested": i < 5
      }

      print("------ {0}".format(m["name_id"]))

      #insert_dex_character_move(dcm)


def scrape_pokemon(character):
  start_gen = character["gen"]

  for g in range(start_gen, 9):
    print("-- Gen {0}".format(g))
    scrape_pokemon_dexes(character, g)


def import_dex_character_moves(start_from = 1):
  characters = get_all_characters()

  tot = len(characters)
  counter = 0

  for c in characters:
    counter += 1
    
    if (counter < start_from):
      continue

    character_id = c["character_id"]
    
    print("{0} {1} ({2})"\
      .format(c["pokemon_id"], c["name"], c["character_id"]))
    
    scrape_pokemon(c)

    print_counter(counter, tot)


all_moves = {}

load_moves()

import_dex_character_moves()