import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import collections

class Character:
    def __init__(self):
        self.dexNumber = ""
        self.name = ""
        self.altForm = ""
        self.types = []
        self.statTotal = 0
        self.hp = 0
        self.attack = 0
        self.defense = 0
        self.specialAttack = 0
        self.specialDefense = 0
        self.speed = 0
        self.imageUrl = ""

def get_page(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(request)
    return response.read()

def get_table_rows(id):
    selector = "#" + id + " > tbody"
    return soup.select_one(selector).find_all("tr")

def create_character_from_row(row):
    c = Character()
    columns = row.find_all("td")
    c.imageUrl = columns[0].select_one(".icon-pkmn").attrs["data-src"]
    
    dexId = columns[0].select_one(".infocard-cell-data").get_text().lstrip("0")
    c.dexNumber = int(dexId)
    
    c.name = columns[1].select_one(".ent-name").get_text()
    altText = columns[1].select_one("small")
    
    if not (altText is None):
        c.altForm = altText.get_text()

    c.statTotal = int(columns[3].get_text())
    c.hp = int(columns[4].get_text())
    c.attack = int(columns[5].get_text())
    c.defense = int(columns[6].get_text())
    c.specialAttack = int(columns[7].get_text())
    c.specialDefense = int(columns[8].get_text())
    c.speed = int(columns[9].get_text())

    cTypes = columns[2].select("a")
    for t in cTypes:
        c.types.append(t.get_text())

    return c

def print_character(ch):
    print("{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8},".format(ch.dexNumber, ch.name, ch.statTotal, ch.hp, ch.attack, ch.defense, ch.specialAttack, ch.specialDefense, ch.speed))
    print(ch.imageUrl)
    print(", ".join(ch.types))


def insert_character(c):
    client = MongoClient(host='localhost', port=27017)
    db = client.pokedex
    r = db.characters.insert_one(c.__dict__)

    return r.inserted_id



url = "https://pokemondb.net/pokedex/all"
soup = BeautifulSoup(get_page(url), "html.parser")

rows = get_table_rows("pokedex")
tot = len(rows)
ctr = 0

for r in rows:
    character = create_character_from_row(r)
    characterId = insert_character(character)
    ctr += 1
    print("{0}/{1} - {2}".format(ctr, tot, characterId))
