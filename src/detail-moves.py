import urllib.request
import collections
import re

from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient(host='localhost', port=27017)
db = client.pokedex

game_generations = {}
type_colors = {
    "Normal": "#d3d3d3",
    "Fire": "#e38c2d",
    "Water": "#0077be",
    "Electric": "#ffff33",
    "Grass": "#32cd32",
    "Ice": "#dcf3ff",
    "Fighting": "#800000",
    "Poison": "#b70df2",
    "Ground": "#e0c068",
    "Flying": "#a4c2f4",
    "Psychic": "#ff007f",
    "Bug": "#7ec850",
    "Rock": "#9b7653",
    "Ghost": "#593d75",
    "Dragon": "#2e2be2",
    "Dark": "#2b1d0e",
    "Steel": "#a7a7a7",
    "Fairy": "#ffb6c1"
}

class CharacterMove:
    def __init__(self, name):
        self.moveId = self.generate_moveId(name)
        self.name = name
        self.isSuggested = False
        self.color = ""
        self.power = 0
        self.accuracy = 0

    def generate_moveId(self, name):
        return name\
            .replace(",", "")\
            .replace("'", "")\
            .replace(" ", "-")\
            .lower()


def get_page(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(request)
    return response.read()


def make_detail_url(name):
    return 'https://pokemondb.net/pokedex/' + name


def make_detail_moves_by_gen_url(name, gen):
    return make_detail_url(name) + '/moves/{0}'.format(gen)


def get_detail_page(name):
    url = make_detail_url(name)
    page = BeautifulSoup(get_page(url), "html.parser")
    return page


def get_detail_moves_by_gen_page(name, gen):
    url = make_detail_moves_by_gen_url(name, gen)
    page = BeautifulSoup(get_page(url), "html.parser")
    return page


def get_nameId(name):
    return name.replace(':', '')\
        .replace(' ', '-')\
        .replace(u'\u2642', '-m')\
        .replace(u'\u2640', '-f')\
        .replace('.', '')\
        .replace(u'\u00E9', 'e')\
        .lower()


def get_game_detail(gameId):
    if gameId in game_generations:
        return game_generations[gameId]
    
    game = db.games.find_one({"gameId": gameId})
    game_generations[gameId] = game

    return game_generations[gameId]


def scrape_moves(game, page):
    # find out which tabs are on this page
    # ex: Red/Blue, Yellow
    # these should both match to Red/Blue/Yellow
    # add all moves and filter to only distinct
    moves = {}
    
    for tab in page.select(".tabs-tab"):
        if tab.get_text() in game["name"]:
            tab_data = page.select_one(tab.attrs["href"])
            scrape_moves_data(tab_data, moves)

    return list(moves.values())


def scrape_moves_data(tab, moves):
    tables = tab.select(".data-table")

    for tbl in tables:
        head1  = tbl.select_one("thead > tr > th > .sortwrap").get_text()
        
        if head1 in ["Lv.", "HM", "TM"]:

            for row in tbl.select("tbody > tr"):
                columns = row.find_all("td")
                
                m = CharacterMove(columns[1].get_text())
                
                move_type = columns[2].select_one("a").get_text()
                m.color = type_colors[move_type]
                m.power = text_to_int(columns[4].get_text())
                m.accuracy = text_to_int(columns[5].get_text())

                if not (m.moveId in moves):
                    moves[m.moveId] = m.__dict__


def text_to_int(text):
    val = text.replace(chr(8212), "").replace(chr(8734), "1000")
    
    if val == "":
        return None
    else:
        return int(val)


results = db.characters.find({ 'altForm': '' })

tot = results.count()
ctr = 0

for c in results:
    c_name = c["name"]
    print(c_name)

    nameId = get_nameId(c_name)
    
    for i, g in enumerate(c["games"]):
        g_id = g["gameId"]
        g_detail = get_game_detail(g_id)
        page = get_detail_moves_by_gen_page(nameId, g_detail["generation"])
        moves = scrape_moves(g_detail, page)
        
        result = db.character_moves.update_many(
            { "name": c_name, "gameId": g_id },
            { "$set": { "moves": moves } },
            upsert=True)
        
        print(g_id, result.matched_count)


    ctr += 1
    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))
