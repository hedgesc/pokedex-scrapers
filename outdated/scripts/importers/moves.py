import urllib.request
from bs4 import BeautifulSoup
import collections
import psycopg2
import psycopg2.extras

# name_id varchar(50) unique not null,
# name varchar(50) not null,
# power int null, 
# accuracy int null, 
# pp int null, 
# generation int not null,
# type varchar(50) not null

connection_string_local = "dbname='pokemondb' user='postgres' host='127.0.0.1' password='Super*32'"
connection_string_prod  = "dbname='pokemondb' user='pi' host='10.0.0.42' password='Super*32'"

class Move:
  def __init__(self):
    self.nameId = ""
    self.name = ""
    self.power = None
    self.accuracy = None
    self.pp = None
    self.gen = 0
    self.type = ""


def get_page(url):
  request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  response = urllib.request.urlopen(request)
  return response.read()


def parse_moves_page(gen):
  url = 'https://pokemondb.net/move/generation/{0}'.format(gen)
  soup = BeautifulSoup(get_page(url), "html.parser") 
  return soup


def insert_move_list(move_list):
  sql = """ INSERT INTO moves(name,name_id,gen,type,power,accuracy,pp) 
  VALUES(%(name)s,%(nameId)s,%(gen)s,%(type)s,%(power)s,%(accuracy)s,%(pp)s) """

  conn = None
  
  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string_local)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.executemany(sql, move_list)
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


def create_move_from_tag(tag, gen):
  columns = tag.find_all("td")

  result = Move()

  result.gen = gen
  result.name = columns[0].select_one(".ent-name").get_text()
  result.nameId = result.name.replace(",", "").replace("'", "").replace(" ", "-").lower()
  result.power = text_to_int(columns[3].get_text())
  result.accuracy = text_to_int(columns[4].get_text())
  result.pp = text_to_int(columns[5].get_text())
  result.type = columns[1].select_one("a").get_text()

  return result


def text_to_int(text):
  val = text.replace(chr(8212), "").replace(chr(8734), "1000")
    
  if val == "":
    return None
  else:
    return int(val)


def move_to_csv_line(move):
  return "{0},\"{1}\",{2},{3},{4},{5},{6}".format(\
    move.nameId, move.name,\
    "" if move.power is None else move.power,\
    "" if move.accuracy is None else move.accuracy,\
    "" if move.pp is None else move.pp,\
    move.gen, move.type)


def print_move(move):
  print(move_to_csv_line(move))


def get_generations():
  return range(1, 9)


moves = []

for g in get_generations():
  print("Importing generation {0} moves".format(g))
  print()

  gen = g
  page = parse_moves_page(gen)
  rows = page.select("#moves > tbody > tr")

  tot = len(rows)
  ctr = 0

  for r in rows:
    move = create_move_from_tag(r, g)

    if not (move is None):
      moves.append(move.__dict__)
      print_move(move)
        
    ctr += 1
    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))

  success = insert_move_list(moves)

  if success:
    moves.clear()

  print()