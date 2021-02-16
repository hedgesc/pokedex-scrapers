import collections
import psycopg2
import psycopg2.extras
import urllib.request
from bs4 import BeautifulSoup


connection_string = "dbname='pokemondb' user='postgres' host='127.0.0.1' password='Super*32'"
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


def insert_dex_character_move(dex_id, character_id, move_id, is_suggested):
  sql = """ 
    INSERT INTO dexes_characters_moves
      (dex_id, character_id, move_id, is_suggested)
    VALUES
      (%s, %s, %s, %s)
  """
  
  conn = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, (dex_id, character_id, move_id, is_suggested,))
    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return False
  finally:
    if conn is not None:
      conn.close()
  
  return True


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


def get_all_dexes_characters():
  sql = """
    select
      c.character_id,
      c.pokemon_id,
      case 
        when c.alternate_name is not null then c.alternate_name 
        else c.name 
      end as character_name,
      c.name_id as character_name_id,
      d.dex_id,
      d.name as dex_name,
      d.name_id as dex_name_id,
      d.gen
    from
      characters c
      join dexes_characters dc
        on c.character_id = dc.character_id
      join dexes d
        on dc.dex_id = d.dex_id
    order by
      c.character_id, d.gen
  """

  conn = None
  dexex_characters = []

  try:
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    dexex_characters = cur.fetchall()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
    
  return dexex_characters


def get_move_nameId(name):
  return name\
    .replace(",", "")\
    .replace("'", "")\
    .replace(" ", "-")\
    .lower()


def get_move_id_by_name_id(name_id):
  return all_moves[name_id]


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


def scrape_dex_moves(scraper, panel_id, dc):
  moves = []

  panel = scraper.select_one(panel_id)

  panel_tables = panel.select(".grid-col > .resp-scroll > .data-table")
  
  form_panels = find_form_panels(panel, dc["character_name"])

  for id_tag in form_panels:
    tables = panel.select_one(id_tag).select(".resp-scroll > .data-table")
    panel_tables.extend(tables)

  counter = 0

  for tbl in panel_tables:
    head1  = tbl.select_one("thead > tr > th > .sortwrap").get_text()
    if head1 in ["Lv.", "HM", "TM", "TR"]:
      counter = counter + 1
      for row in tbl.select("tbody > tr"):
        columns = row.find_all("td")
        num = text_to_int(columns[0].get_text())
        move_name = columns[1].get_text()
        move_name_id = get_move_nameId(move_name)
        power = text_to_int(columns[4].get_text())
        move_info = {
          "n": num,
          "name": move_name,
          "name_id": move_name_id, 
          "power": power 
        }
        moves.append(move_info)

  moves.sort(key = lambda m: (m["power"], m["n"]), reverse = True)
  return moves


def find_form_panels(panel, name):
  results = []

  tabsets = panel.select(".tabset-moves-game-form")
  
  for tabset in tabsets:
    tablist = tabset.select_one(".sv-tabs-tab-list")
    tabs = tablist.select(".sv-tabs-tab")
    for tab in tabs:
      if tab.get_text() == name:
        results.append(tab["href"])
        break

  return results

def find_moves_panel(url, scraper, dc):
  if not (url in cached_tabs):
    tabset = scraper.select_one(".tabset-moves-game > .sv-tabs-tab-list")
    cached_tabs[url] = tabset.select(".sv-tabs-tab")

  result = None

  for tab in cached_tabs[url]:
    if tab.get_text() == dc["dex_name"]:
      result = tab["href"]
      break

  return result


def import_dex_character_moves(dc):
  url = "https://pokemondb.net/pokedex/{0}/moves/{1}"\
    .format(dc["character_name_id"], dc["gen"])
  
  scraper = build_scraper(url)

  panel_id = find_moves_panel(url, scraper, dc)

  moves = scrape_dex_moves(scraper, panel_id, dc)

  index = 0
  for move in moves:
    move_id = get_move_id_by_name_id(move["name_id"])
    
    if move_id is None:
      continue

    is_suggested = index < 4

    text = "  {0} {1} ({2})".format(move_id, move["name"], move["n"])

    if is_suggested:
      text += " (suggested)"

    print(text)

    success = insert_dex_character_move(dc["dex_id"], dc["character_id"], move_id, is_suggested)
    
    if success:
      index += 1
  


def import_moves(start_from = 1, end_at = None):
  dexes_characters = get_all_dexes_characters()

  tot = len(dexes_characters)
  counter = 0

  for dc in dexes_characters:
    counter += 1
    
    if (counter < start_from):
      continue

    print("{0} {1} ({2}) - {3} {4}".format(dc["character_id"], dc["character_name"], dc["pokemon_id"], dc["dex_id"], dc["dex_name"]))
    
    import_dex_character_moves(dc)

    print_counter(counter, tot)

    if not (end_at is None) and counter >= end_at:
      break

all_moves = {}
cached_tabs = {}

# start program
load_moves()
import_moves()