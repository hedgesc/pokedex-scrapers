import collections
import psycopg2
import psycopg2.extras
import urllib.request
from bs4 import BeautifulSoup
import pprint

list_url = "https://pokemondb.net/pokedex/all"
base_detail_url = "https://pokemondb.net/pokedex/"
connection_string = "dbname='pokemondb' user='postgres' host='localhost' password='Super*32'"
# pi-zero
# connection_string  = "dbname='pokemondb' user='pi' host='10.0.0.42' password='Super*32'"

# classes
class DexCharacterMove:
  def __init__(self, dex_character_id, move_id, is_suggested):
    self.dexCharacterId = dex_character_id
    self.moveId = move_id
    self.isSuggested = is_suggested

class DexCharacter:
  def __init__(self, dex_id, character_id):
    self.dexId = dex_id
    self.characterId = character_id

class Character:
  baseImageUrl = "https://www.serebii.net/swordshield/pokemon/"
  baseImageExt = ".png"
  characterId = None
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
      .lower()

  def setImageUrl(self):
    self.imageUrl = "{0}{1:03d}{2}".format(
      self.baseImageUrl, 
      self.characterId, 
      self.baseImageExt)
# classes end

# sql
def insert_character(character):
  sql = """ 
  INSERT INTO characters(
    character_id, name, name_id, image_url, types,
    abilities, gen, hp, attack, defense, special_attack,
    special_defense, speed, total)
  VALUES(
    %(characterId)s, %(name)s, %(nameId)s, %(imageUrl)s, %(types)s,
    %(abilities)s, %(gen)s, %(hp)s, %(attack)s, %(defense)s, %(specialAttack)s,
    %(specialDefense)s, %(speed)s, %(total)s) 
  ON CONFLICT (character_id) DO UPDATE SET
  (character_id, name, name_id, image_url, 
  types, abilities, gen, hp, attack, defense, 
  special_attack, special_defense, speed, total) = 
  (EXCLUDED.character_id, EXCLUDED.name, EXCLUDED.name_id, EXCLUDED.image_url, 
  EXCLUDED.types, EXCLUDED.abilities, EXCLUDED.gen, EXCLUDED.hp, EXCLUDED.attack, EXCLUDED.defense, 
  EXCLUDED.special_attack, EXCLUDED.special_defense, EXCLUDED.speed, EXCLUDED.total) 
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

def insert_dex_character(dexCharacter):
  sql = """ 
  INSERT INTO dexes_characters (dex_id, character_id)
  VALUES (%(dexId)s,%(characterId)s) 
  ON CONFLICT (dex_id, character_id) 
  DO UPDATE SET (dex_id, character_id) = 
    (EXCLUDED.dex_id, EXCLUDED.character_id) 
  RETURNING dex_character_id; """
  
  conn = None
  dexCharacterId = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, dexCharacter.__dict__)
    # get the generated id back
    dexCharacterId = cur.fetchone()[0]
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

  return dexCharacterId

def insert_dex_character_move(dexCharacterMove):
  sql = """ 
    INSERT INTO dex_character_moves(dex_character_id,move_id,is_suggested)
    VALUES(%(dexCharacterId)s,%(moveId)s,%(isSuggested)s) 
    ON CONFLICT (dex_character_id, move_id) DO NOTHING;
  """
  
  conn = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, dexCharacterMove.__dict__)
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

def get_dexId_by_nameId(nameId):
  sql = """ select dex_id from dexes where name_id = %s """
  conn = None
  dexId = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string)
    # create a new cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # execute the sql statement
    cur.execute(sql, (nameId,))
    # get result
    rec = cur.fetchone()
    # close communication with the database
    cur.close()

    if rec is None:
      dexId = None
    
    # return dexId
    dexId = rec[0]
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return None
  finally:
    if conn is not None:
      conn.close()

  return dexId

def get_moveId_by_nameId(nameId):
  sql = """ select move_id from moves where name_id = %s """
  
  conn = None
  moveId = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string)
    # create a new cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # execute the sql statement
    cur.execute(sql, (nameId,))
    # get result
    rec = cur.fetchone()
    # close communication with the database
    cur.close()

    if rec is None:
      moveId = None
    
    # return moveId
    moveId = rec[0]
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return None
  finally:
    if conn is not None:
      conn.close()

  return moveId
# sql end

# helper functions
def detail_page_url(nameId):
  return base_detail_url + nameId

def make_detail_moves_by_gen_url(baseUrl, gen):
  return baseUrl + "/moves/{0}".format(gen)

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

def get_move_nameId(name):
  return name\
    .replace(",", "")\
    .replace("'", "")\
    .replace(" ", "-")\
    .lower()
# helper functions end

# scraping
def text_to_int(text):
  val = text.replace(chr(8212), "").replace(chr(8734), "1000")
    
  if val == "":
    return 0
  else:
    return int(val)

def get_table_rows(url, tableId):
  soup = build_scraper(url)
  selector = "#" + tableId + " > tbody"
  return soup.select_one(selector).find_all("tr")

def create_character_from_row(row):
  columns = row.find_all("td")

  altText = columns[1].select_one("small")
    
  if not (altText is None):
    return None

  result = Character()
  
  result.characterId = int(columns[0].select_one(".infocard-cell-data").get_text().lstrip("0"))
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

def get_abilities_row(character_detail_url):
  soup = build_scraper(character_detail_url)

  abilities_row = None

  for row in soup.select(".vitals-table tr"):
    head = row.find("th")
      
    if head is None:
      continue
      
    if (head.get_text() == "Abilities"):
      abilities_row = row
      break

  return abilities_row

def get_character_gen(url):
  gen = None
  is_gen_list = False
  scraper = build_scraper(url)
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
    return 8
    
  return int(gen)

def detail_moves_by_gen_page(baseUrl, gen):
  url = make_detail_moves_by_gen_url(baseUrl, gen)
  page = build_scraper(url)
  return page

def scrape_moves(scraper, tabs_panel_id):
  moves = []

  panel = scraper.select_one(tabs_panel_id)
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

character_rows = get_table_rows(list_url, "pokedex")
tot = len(character_rows)
ctr = 0

for r in character_rows:
  ctr += 1

  character = create_character_from_row(r)

  if character is None:
    print ("Skipping row {0}; character is an alternate form.".format(ctr))
    print("{0}/{1}".format(ctr, tot))
    print()
    continue

  print("importing character {0} - {1} from row {2}".format(character.characterId, character.name, ctr))

  # get character detail page
  character_detail_url = detail_page_url(character.nameId)
  
  # get character gen
  character.gen = get_character_gen(character_detail_url)

  # scrape abilities
  abilities_row = get_abilities_row(character_detail_url)

  if not (abilities_row is None):
    ability_links = abilities_row.find("td").select("a")

    for link in ability_links:
      character.abilities.append(link.get_text())

  # insert character
  character_id = insert_character(character)
  print("importing character {0}: success".format(character_id))
  # print character
  print()
  pprint.pprint(character.__dict__)
  print()

  for gen in range(character.gen, 9):
    print("\tattaching character {0} to pokedexes from gen {1}".format(character_id, gen))

    moves_scraper = detail_moves_by_gen_page(character_detail_url, gen)

    for tab in moves_scraper.select(".tabs-tab"):
      dex_name = tab.get_text()
      dex_name_id = get_dex_nameId(dex_name)
      dex_id = get_dexId_by_nameId(dex_name_id)
      dex_character = DexCharacter(dex_id, character_id)
      
      dex_character_msg = "\tattaching character {0} to pokedex {1}".format(character_id, dex_name)
      print(dex_character_msg)

      # insert dex character
      dex_character_id = insert_dex_character(dex_character)

      if dex_character_id is None:
        print(dex_character_msg + " failed")
        break
      
      print(dex_character_msg + ", id = {0}".format(dex_character_id))
      print()

      tab_panel_id = tab["href"]

      moves = scrape_moves(moves_scraper, tab_panel_id)
      
      print("\t\tattaching {0} moves to character {1} in pokedex {2}".format(len(moves), character_id, dex_name))
      
      i = 0
      for move_info in moves:
        move_id = get_moveId_by_nameId(move_info["name_id"])

        if move_id is None:
          continue

        dex_character_move = DexCharacterMove(dex_character_id, move_id, i < 4)
        
        insert_dex_character_move(dex_character_move)

        i += 1

      print("\t\tdone.")

  print("{0}/{1}".format(ctr, tot))
  print()