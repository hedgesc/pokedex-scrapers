import collections
import psycopg2
import psycopg2.extras
import urllib.request
from bs4 import BeautifulSoup
import pprint

connection_string = "dbname='pokemondb' user='postgres' host='localhost' password='Super*32'"
# pi-zero
# connection_string  = "dbname='pokemondb' user='pi' host='10.0.0.42' password='Super*32'"

class Character:
  def __init__(self):
    self.pokemonId = None
    self.name = None
    self.total = None
    self.hp = None
    self.attack = None
    self.defense = None
    self.specialAttack = None
    self.specialDefense = None
    self.speed = None
    self.nameId = None
    self.alternateName = None
    self.types = []
    self.abilities = []
    self.isAlternateForm = False

  def getDetailUrl(self):
    base_url = "https://pokemondb.net/pokedex/"

    return base_url + self.nameId

def generate_nameId_from_name(name):
  return name.replace(":", "")\
    .replace(" ", "-")\
    .replace(u'\u2642', '-m')\
    .replace(u'\u2640', '-f')\
    .replace(".", "")\
    .replace(u'\u00E9', 'e')\
    .replace("'", "")\
    .lower()


def insert_character(character):
  sql = """ 
  INSERT INTO characters(
    pokemon_id, name, name_id, types, abilities, hp, 
    attack, defense, special_attack, special_defense, 
    speed, total, alternate_name)
  VALUES(
    %(pokemonId)s, %(name)s, %(nameId)s, %(types)s, %(abilities)s, %(hp)s, 
    %(attack)s, %(defense)s, %(specialAttack)s, %(specialDefense)s, 
    %(speed)s, %(total)s, %(alternateName)s) 
  ON CONFLICT (character_id) DO NOTHING 
  RETURNING character_id; """
  
  conn = None
  characterId = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, character.__dict__)
    # get the generated id back
    characterId = cur.fetchone()[0]
    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return None
  finally:
    if conn is not None:
      conn.close()

  return characterId

# potentially a module candidate
def get_page(url):
  request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  response = urllib.request.urlopen(request)
  return response.read()

def build_scraper(url):
  return BeautifulSoup(get_page(url), "html.parser")


def scrape_pokemon_detail_dex_data(character, panel):
  types = []
  abilities = []

  table = panel.select_one(".vitals-table")
  rows = table.select("tr")

  for row in rows:
    head = row.select_one("th")
    
    if head is None:
      continue

    head_text = head.get_text()

    if head_text == "Type":
      cell = row.select_one("td")
      
      if not (cell is None):
        for t in cell.select("a"):
          types.append(t.get_text())

    if head_text == "Abilities":
      cell = row.select_one("td")

      if not (cell is None):
        for a in cell.select("a"):
          abilities.append(a.get_text())

  if len(character.types) == 0:
    character.types = types

  if len(character.abilities) == 0:
    character.abilities = abilities


def find_detail_panel(scraper, character):
  result = None
  text = None

  if character.isAlternateForm:
    text = character.alternateName
  else:
    text = character.name

  tabs = scraper.select(".tabset-basics > .tabs-tab-list > .tabs-tab")

  for tab in tabs:
    if tab.get_text() == text:
      result = scraper.select_one(tab["href"])
      break

  return result


def scrape_pokemon_detail(character):
  detail_url = character.getDetailUrl()
  scraper = build_scraper(detail_url)
  panel = find_detail_panel(scraper, character)
  scrape_pokemon_detail_dex_data(character, panel)


def scrape_pokemon_item(elem):
  columns = elem.find_all("td")

  result = Character()
  result.pokemonId = columns[0].select_one(".infocard-cell-data").get_text()

  result.name = columns[1].select_one(".ent-name").get_text()
  result.nameId = generate_nameId_from_name(result.name)
  
  alt_name_tag = columns[1].select_one("small")
  
  if not (alt_name_tag is None):
    result.alternateName = alt_name_tag.get_text()
    result.isAlternateForm = True

  for t in columns[2].select("a"):
      result.types.append(t.get_text())

  result.total = int(columns[3].get_text())
  result.hp = int(columns[4].get_text())
  result.attack = int(columns[5].get_text())
  result.defense = int(columns[6].get_text())
  result.specialAttack = int(columns[7].get_text())
  result.specialDefense = int(columns[8].get_text())
  result.speed = int(columns[9].get_text())

  return result

def scrape_all_pokemon(start_row = 0):
  url = "https://pokemondb.net/pokedex/all"

  scraper = build_scraper(url)

  rows = scraper.select("#pokedex > tbody > tr")

  tot = len(rows)
  row_counter = 0

  for r in rows:
    row_counter += 1

    if (row_counter < start_row):
      continue

    print("Importing character in row {0}".format(row_counter))

    character = scrape_pokemon_item(r)
    
    if character.isAlternateForm:
      print("-- {0} - {1} ({2})".format(character.pokemonId, character.name, character.alternateName))
    else:
      print("-- {0} - {1}".format(character.pokemonId, character.name))

    print("---- {0}%  Complete".format(85))

    scrape_pokemon_detail(character)
    print("---- {0}%  Complete".format(92))

    character_id = insert_character(character)
    print("---- {0}% Complete".format(100))

    print("{0}/{1} Done".format(row_counter, tot))
    print()


scrape_all_pokemon()
