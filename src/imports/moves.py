import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import collections

# name_id varchar(50) unique not null,
# name varchar(50) not null,
# category varchar(50) null, 
# power int null, 
# accuracy int null, 
# pp int null, 
# generation int not null,
# type varchar(50) not null

class Move:
  def __init__(self):
    self.nameId = ""
    self.name = ""
    self.category = ""
    self.power = 0
    self.accuracy = 0
    self.pp = 0
    self.generation = 0
    self.type = ""


def get_page(url):
  request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  response = urllib.request.urlopen(request)
  return response.read()


def parse_moves_page(gen):
  url = 'https://pokemondb.net/move/generation/{0}'.format(gen)
  soup = BeautifulSoup(get_page(url), "html.parser") 
  return soup


def insert_move(move):
  client = MongoClient(host='localhost', port=27017)
  db = client.pokedex
  result = db.moves.insert_one(move.__dict__)
  return result.inserted_id


def create_move_from_tag(tag):
  columns = tag.find_all("td")

  cat = columns[2].attrs["data-filter-val"]

  if cat == '':
    return None

  result = Move()

  result.name = columns[0].select_one(".ent-name").get_text()
  result.nameId = result.name.replace(",", "").replace("'", "").replace(" ", "-").lower()
  result.category = cat
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
  return "{0},\"{1}\",{2},{3},{4},{5},{6},{7}".format(\
    move.nameId, move.name, move.category,\
    "" if move.power is None else move.power,\
    "" if move.accuracy is None else move.accuracy,\
    "" if move.pp is None else move.pp,\
    move.generation, move.type)


def print_move(move):
  print(move_to_csv_line(move))


def make_csv(data):
  csv = open("moves.csv", "w")
  csv.truncate(0)

  header = "name_id,name,category,power,accuracy,pp,generation,type\n"
  csv.write(header)

  for m in data:
    csv.write(move_to_csv_line(m) + "\n")
  
  csv.close()


def get_generations():
  return range(1, 9)


moves = []

for g in get_generations():
  print("Getting generation {0} moves".format(g))

  gen = g
  page = parse_moves_page(gen)
  rows = page.select("#moves > tbody > tr")

  tot = len(rows)
  ctr = 0

  for r in rows:
    move = create_move_from_tag(r)

    if not (move is None):
      move.generation = gen
      moves.append(move)
      print_move(move)
        
    ctr += 1
    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))

make_csv(moves)