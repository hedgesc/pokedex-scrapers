import urllib.request
import collections
import re
from bs4 import Tag, NavigableString, BeautifulSoup
import psycopg2
import psycopg2.extras


class CharacterGame:
  def __init__(self):
    self.characterId = 0
    self.gameId = 0
    self.gameCharacterId = 0
    self.generation = 0


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


def game_characters_page(pageId):
  url = 'https://pokemondb.net/pokedex/game/' + pageId
  soup = BeautifulSoup(get_page(url), "html.parser")
  return soup


def cg_to_csv(c):
  return "{0},{1},{2},{3}".format(c.characterId, c.gameId, c.gameCharacterId, c.generation)


csv = open("character_games.csv", "w", encoding='utf-8')
csv.truncate(0)

header = "character_id,game_id,game_character_id,generation\n"
csv.write(header)

try:
  conn = psycopg2.connect("dbname='pokedex' user='postgres' host='localhost' password='Super*32'")
except:
  print("I am unable to connect to the database")

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

try:
  cur.execute("select * from game_groups order by game_group_id")
except:
  print("I can't SELECT from game_groups")

rows = cur.fetchall()

for row in rows:
  page = game_characters_page(row['name_id'])
  cards = page.select('.infocard')

  for c in cards:
    data = c.select_one(".infocard-lg-data > small")
    
    if data is None:
      continue

    dexNumText = data.get_text().replace("#", "0").lstrip("0")

    if dexNumText == '':
      localDexNum = 0
    else:
      localDexNum = int(dexNumText)

    name = c.select_one(".ent-name").get_text()
    nameId = get_nameId(name)

    cur.execute("select * from characters where name_id = %s", (nameId,))
    char = cur.fetchone()

    sql = "select games.game_id, games.generation "\
      "from game_group_games "\
      "join games on game_group_games.game_id = games.game_id "\
      "where game_group_games.game_group_id = %s"

    cur.execute(sql, (row['game_group_id'],))
    gms = cur.fetchall()

    for gm in gms:
      cg = CharacterGame()
      cg.characterId = char['character_id']
      cg.gameId = gm['game_id']
      cg.gameCharacterId = localDexNum
      cg.generation = gm['generation']

      csv_line = cg_to_csv(cg)
      print(csv_line)

      csv.write(csv_line + "\n")


conn.close()
csv.close()