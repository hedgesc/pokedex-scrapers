import urllib.request
import collections
import re

from bs4 import Tag, NavigableString, BeautifulSoup
#from pymongo import MongoClient

'''
{
  "dexNumber" : NumberInt(1), 
  "name" : "Bulbasaur", 
  "altForm" : "", 
  "types" : [
    "Grass", 
    "Poison"
  ], 
  "statTotal" : NumberInt(318), 
  "hp" : NumberInt(45), 
  "attack" : NumberInt(49), 
  "defense" : NumberInt(49), 
  "specialAttack" : NumberInt(65), 
  "specialDefense" : NumberInt(65), 
  "speed" : NumberInt(45), 
  "imageUrl" : "https://img.pokemondb.net/sprites/omega-ruby-alpha-sapphire/dex/normal/bulbasaur.png", 
  "games" : [
    {
        "gameDexId" : NumberInt(1), 
        "gameId" : "red-blue-yellow", 
        "moves" : [

        ]
    }
  ], 
  "nameId" : "bulbasaur", 
  "generation" : NumberInt(1)
}
'''

# national_dex_id int not null,
# name_id varchar (50) unique not null,
# "name" varchar (50) not null,
# hp int not null,
# attack int not null,
# defense int not null,
# special_attack int not null,
# special_defense int not null,
# speed int not null,
# total int not null,
# image_url varchar(255) not null,
# generation int not null,
# "types" text[] not null

class Character:
  def __init__(self):
    self.dexNumber = 0
    self.nameId = ""
    self.name = ""
    self.hp = 0
    self.attack = 0
    self.defense = 0
    self.specialAttack = 0
    self.specialDefense = 0
    self.speed = 0
    self.total = 0
    self.imageUrl = ""
    self.generation = 0
    self.types = []

def get_nameId(name):
  return name.replace(':', '')\
    .replace(' ', '-')\
    .replace(u'\u2642', '-m')\
    .replace(u'\u2640', '-f')\
    .replace('.', '')\
    .replace(u'\u00E9', 'e')\
    .replace('\'', '')\
    .lower()


def get_page(url):
  request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  response = urllib.request.urlopen(request)
  return response.read()


def national_page():
  url = 'https://pokemondb.net/pokedex/national'
  soup = BeautifulSoup(get_page(url), "html.parser") 
  return soup


def get_character_detail_page(nameId):
  url = 'https://pokemondb.net/pokedex/' + nameId
  soup = BeautifulSoup(get_page(url), "html.parser")
  return soup


def build_character_from_card(c):
  result = Character()

  result.imageUrl = c.select_one(".img-sprite").attrs["data-src"]

  data = c.select_one(".infocard-lg-data > small")
    
  if data is None:
    return None

  result.dexNumber = int(data.get_text().replace("#", "0").lstrip("0"))

  a_name = c.select_one(".ent-name")
  result.name = a_name.get_text()
  result.nameId = get_nameId(result.name)

  types = []

  for t in c.select('.itype'):
    types.append(t.get_text())

  result.types = types

  return result


def scrape_characters(page):
  csv = open("characters.csv", "w", encoding='utf-8')
  csv.truncate(0)

  header = "character_id,name_id,name,hp,attack,defense,special_attack,special_defense,speed,total,image_url,generation,types\n"

  csv.write(header)

  gen = 1
  gens = page.select('.infocard-list')

  for g in gens:
    print('processing generation {0}'.format(gen))
    print()

    cards = g.select('.infocard')

    for c in cards:
      char = build_character_from_card(c)

      if char is None:
        continue

      print("\t{0} - {1} ...parsing".format(char.dexNumber, char.nameId))

      char.generation = gen

      detail_page = get_character_detail_page(char.nameId)

      dex_stats = detail_page.select_one('#dex-stats ~ .resp-scroll')
      stats_tbl = dex_stats.select_one('.vitals-table')
      rows = stats_tbl.select('tr')

      for r in rows:
        h = r.select_one('th').get_text()
        n = r.select('td')[0].get_text()

        if(h == 'HP'):
          char.hp = int(n)
        elif(h == 'Attack'):
          char.attack = int(n)
        elif(h == 'Defense'):
          char.defense = int(n)
        elif(h == 'Sp. Atk'):
          char.specialAttack = int(n)
        elif(h == 'Sp. Def'):
          char.specialDefense = int(n)
        elif(h == 'Speed'):
          char.speed = int(n)
        elif(h == 'Total'):
          char.total = int(n)

      csv.write(character_to_csv(char) + "\n")

    gen = gen + 1
    print()

  csv.close()

# self.dexNumber = 0
# self.nameId = ""
# self.name = ""
# self.hp = 0
# self.attack = 0
# self.defense = 0
# self.specialAttack = 0
# self.specialDefense = 0
# self.speed = 0
# self.total = 0
# self.imageUrl = ""
# self.generation = 0
# self.types = []


def character_to_csv(c):
  _types = ','.join(c.types) if len(c.types) > 1 else c.types[0]

  return "{0},{1},\"{2}\",{3},{4},{5},{6},{7},{8},{9},\"{10}\",{11},\"{{{12}}}\""\
    .format(c.dexNumber, c.nameId, c.name, c.hp, c.attack,\
      c.defense, c.specialAttack, c.specialDefense, c.speed,\
        c.total, c.imageUrl, c.generation, _types)


def print_character(c):
  print(character_to_csv(c))


scrape_characters(national_page())
print("\nDone.")
