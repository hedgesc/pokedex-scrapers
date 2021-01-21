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
  baseImageUrl = "https://www.serebii.net/swordshield/pokemon/"
  baseImageExt = ".png"
  pokemonId = None
  name = None
  types = None
  total = None
  hp = None
  attack = None
  defense = None
  specialAttack = None
  specialDefense = None
  speed = None
  imageUrl = None
  nameId = None
  gen = None
  abilities = None

  def __init__(self):
    self.types = []
    self.abilities = []

  def setNameId(self):
    self.nameId = self.name.replace(":", "")\
      .replace(" ", "-")\
      .replace(u'\u2642', '-m')\
      .replace(u'\u2640', '-f')\
      .replace(".", "")\
      .replace(u'\u00E9', 'e')\
      .replace("'", "")\
      .lower()

  def setImageUrl(self):
    self.imageUrl = "{0}{1}{2}".format(
      self.baseImageUrl, 
      self.pokemonId, 
      self.baseImageExt)

  def setGen(self, n):
    id = int(self.pokemonId.lstrip("0"))

    if n == 0 and id > 809:
      self.gen = 8
    else:
      self.gen = n

  def getDetailUrl(self):
    base_url = "https://pokemondb.net/pokedex/"

    return base_url + self.nameId


def insert_character(character):
  sql = """ 
  INSERT INTO characters(
    pokemon_id, name, name_id, image_url, 
    types, abilities, gen, hp, 
    attack, defense, special_attack, special_defense, 
    speed, total)
  VALUES(
    %(pokemonId)s, %(name)s, %(nameId)s, %(imageUrl)s, 
    %(types)s, %(abilities)s, %(gen)s, %(hp)s, 
    %(attack)s, %(defense)s, %(specialAttack)s, %(specialDefense)s, 
    %(speed)s, %(total)s) 
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

def scrape_gen(scraper):
  gen = None
  is_gen_list = False
  
  unordered_lists = scraper.select("ul")
  
  for ul in unordered_lists:
    line_items = ul.select("li")
    for li in line_items:
      if li.get_text().lower() == "in other generations":
        is_gen_list = True
        break
    if is_gen_list:
      gen = line_items[1].find("a").get_text()
      break
  
  if gen is None:
    return 0
    
  return int(gen)

def scrape_abilities(scraper):
  abilities = []
  
  abilities_row = None

  for row in scraper.select(".vitals-table tr"):
    head = row.find("th")
      
    if head is None:
      continue
      
    if (head.get_text() == "Abilities"):
      abilities_row = row
      break

  if abilities_row is None:
    return abilities

  ability_links = abilities_row.find("td").select("a")

  for link in ability_links:
    abilities.append(link.get_text())

  return abilities

def scrape_pokemon_detail(character):
  url = character.getDetailUrl()
  
  scraper = build_scraper(url)

  character.abilities = scrape_abilities(scraper)
  print("---- {0}%  Complete".format(87))

  gen = scrape_gen(scraper)
  character.setGen(gen)
  print("---- {0}%  Complete".format(93))

def scrape_pokemon_item(elem):
  columns = elem.find_all("td")

  altText = columns[1].select_one("small")
    
  if not (altText is None):
    return None

  result = Character()

  result.pokemonId = columns[0].select_one(".infocard-cell-data").get_text()
  result.name = columns[1].select_one(".ent-name").get_text()

  for t in columns[2].select("a"):
      result.types.append(t.get_text())

  result.total = int(columns[3].get_text())
  result.hp = int(columns[4].get_text())
  result.attack = int(columns[5].get_text())
  result.defense = int(columns[6].get_text())
  result.specialAttack = int(columns[7].get_text())
  result.specialDefense = int(columns[8].get_text())
  result.speed = int(columns[9].get_text())
  
  result.setNameId()
  result.setImageUrl()

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

    if character is None:
      print ("-- Alternate form... skipping.")
      print("{0}/{1} Complete.".format(row_counter, tot))
      print()
      continue
    
    print("-- {0} - {1}".format(character.pokemonId, character.name))
    print("---- {0}%  Complete".format(80))

    scrape_pokemon_detail(character)

    character_id = insert_character(character)
    print("---- {0}% Complete".format(100))

    print("{0}/{1} Complete ({2})".format(row_counter, tot, character_id))
    print()

scrape_all_pokemon()
