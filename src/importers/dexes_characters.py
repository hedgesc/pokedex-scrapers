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
  sql = """ 
    SELECT character_id, pokemon_id, name, name_id, alternate_name
    FROM characters 
    ORDER BY character_id 
  """

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

def get_dexids_from_games(games):
  sql = """
    SELECT DISTINCT dex_id
    FROM dex_games
    WHERE name IN %s
    ORDER BY dex_id
  """

  conn = None
  rows = []
  dexids = []

  try:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute(sql, (games,))
    rows = cur.fetchall()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
  
  for row in rows:
    dexids.append(row[0])

  return dexids


def update_character_gen(character_id, gen):
  sql = """
    UPDATE characters
    SET gen = %s
    WHERE character_id = %s 
  """
  
  conn = None
  success = True

  try:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute(sql, (gen,character_id,))
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    success = False
  finally:
    if conn is not None:
      conn.close()
  
  return success


def get_gen_from_dex_id(dex_id):
  sql = """
    SELECT gen FROM dexes WHERE dex_id = %s
  """

  conn = None
  result = None

  try:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql, (dex_id,))
    result = cur.fetchone()[0]
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
  
  return result

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

# def scrape_pokemon_dexes(character, gen):
#   character_id = character["character_id"]

#   url = "https://pokemondb.net/pokedex/{0}/moves/{1}"\
#       .format(character["name_id"], gen)
    
#   scraper = build_scraper(url)

#   tabset = scraper.select_one(".tabs-tab-list")
#   tabs = tabset.select(".tabs-tab")

#   for tab in tabs:
#     dex_name_id = get_dex_nameId(tab.get_text())
#     dex_id = get_dexId_by_nameId(dex_name_id)
    
#     if dex_id is None:
#       continue

#     print("---- {0} ({1})".format(dex_name_id, dex_id))
    
#     insert_dex_character(dex_id, character_id)


def find_tag_with_value(scraper, selector, value):
  result = None
  
  tags = scraper.select(selector)
  
  for tag in tags:
    if tag.get_text().lower() == value:
      result = tag
      break

  return result


def find_games_table(relative_to_tag, character_name):
  wrapper_tag = None
  is_ok = True

  for sibling in relative_to_tag.next_siblings:
    
    if sibling == '\n':
      continue

    if is_ok and sibling.has_attr("class") and "resp-scroll" in sibling["class"]:
      wrapper_tag = sibling
      break

    is_ok = False

    if sibling.name == "h3" and sibling.get_text() == character_name:
      is_ok = True

  if not (wrapper_tag is None):
    return wrapper_tag.table

  return None


def scrape_pokemon_detail(character):
  url = "https://pokemondb.net/pokedex/{0}".format(character["name_id"])
  
  scraper = build_scraper(url)

  pe_tag = find_tag_with_value(scraper, "h2", "pokédex entries")

  if pe_tag is None:
    return

  games = ()

  name = None

  if not (character["alternate_name"] is None):
    name = character["alternate_name"]
  else:
    name = character["name"]

  table = find_games_table(pe_tag, name)

  if table is None:
    return None

  rows = table.find_all("tr")
  
  for row in rows:
    th = row.find("th")
    spans = th.find_all("span")
    
    for span in spans:
      games = games + (span.get_text(),)

  return games


def import_dexes_characters(start_from = 1):
  characters = get_all_characters()

  tot = len(characters)
  counter = 0

  for c in characters:
    counter += 1
    
    if (counter < start_from):
      continue

    character_id = c["character_id"]
    
    if not (c["alternate_name"] is None):
      print("{0} {1} ({2})".format(c["pokemon_id"], c["name"], c["alternate_name"]))
    else:
      print("{0} {1}".format(c["pokemon_id"], c["name"]))
    
    games = scrape_pokemon_detail(c)

    if games is None:
      continue

    print("-- scraped {0} games".format(len(games)))

    dex_ids = get_dexids_from_games(games)
    print("-- retrieved {0} dexes from {1} games".format(len(dex_ids), len(games)))

    gen = get_gen_from_dex_id(min(dex_ids))

    update_character_gen(character_id, gen)
    print("-- updated character {0}, gen = {1}".format(character_id, gen))

    for dex_id in dex_ids:
      insert_dex_character(dex_id, character_id)

    print("-- added {0} dexes".format(len(dex_ids)))

    print_counter(counter, tot)

    
import_dexes_characters()