import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import collections


class Move:
    def __init__(self):
        self.moveId = ""
        self.name = ""
        self.type = ""
        self.category = ""
        self.power = 0
        self.accuracy = 0
        self.pp = 0
        self.generation = 0


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
    result.moveId = result.name.replace(",", "").replace("'", "").replace(" ", "-").lower()
    result.type = columns[1].select_one("a").get_text()
    result.category = cat
    result.power = text_to_int(columns[3].get_text())
    result.accuracy = text_to_int(columns[4].get_text())
    result.pp = text_to_int(columns[5].get_text())

    return result


def text_to_int(text):
    val = text.replace(chr(8212), "").replace(chr(8734), "1000")
    
    if val == "":
        return None
    else:
        return int(val)


def print_move(move):
    print("{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}".format(\
        move.moveId, move.name, move.type,\
        move.category, move.power, move.accuracy,\
        move.pp, move.generation))


for g in range(1, 8):
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
            print(insert_move(move))
            #print_move(move)
        
        ctr += 1
        print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))