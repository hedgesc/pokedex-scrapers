import collections
import psycopg2
import psycopg2.extras
import urllib.request
from bs4 import BeautifulSoup

base_detail_url = "https://pokemondb.net/pokedex/"
connection_string = "dbname='pokemondb' user='postgres' host='localhost' password='Super*32'"
# pi-zero
# connection_string  = "dbname='pokemondb' user='pi' host='10.0.0.42' password='Super*32'"

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

def insert_dex_character(dex_id, character_id):
  sql = """ 
  INSERT INTO dexes_characters (dex_id, character_id)
  VALUES (%s, %s) 
  ON CONFLICT (dex_id, character_id)
  DO NOTHING; """
  
  conn = None
  
  try:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute(sql, (dex_id, character_id,))
    conn.commit()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()

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
    
    insert_dex_character(dex_id, character_id)


def scrape_pokemon(character):
  start_gen = character["gen"]

  for g in range(start_gen, 9):
    print("-- Gen {0}".format(g))
    scrape_pokemon_dexes(character, g)


def import_dexes_characters(start_from = 1):
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

    
import_dexes_characters()