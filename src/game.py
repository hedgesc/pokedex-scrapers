import urllib.request
import collections
import re

from bs4 import BeautifulSoup
from pymongo import MongoClient


client = MongoClient(host='localhost', port=27017)
db = client.pokedex


class GameData:
    def __init__(self, pageId, gameId):
        self.pageId = pageId
        self.gameId = gameId


class CharacterData:
    def __init__(self, gameDexId, name):
        self.gameDexId = gameDexId
        self.name = name
        self.gameId = 0


game_pages = [
    GameData("lets-go-pikachu-eevee", "letsgopikachu-letsgoeevee"),
    GameData("ultra-sun-ultra-moon", "u.sun-u.moon"),
    GameData("sun-moon", "sun-moon"),
    GameData("omega-ruby-alpha-sapphire", "omegaruby-alphasapphire"),
    GameData("x-y", "x-y"),
    GameData("black-white-2", "black2-white2"),
    GameData("black-white", "black-white"),
    GameData("heartgold-soulsilver", "heartgold-soulsilver"),
    GameData("platinum", "platinum"),
    GameData("diamond-pearl", "diamond-pearl"),
    GameData("firered-leafgreen", "firered-leafgreen"),
    GameData("ruby-sapphire-emerald", "ruby-sapphire-emerald"),
    GameData("gold-silver-crystal", "gold-silver-crystal"),
    GameData("red-blue-yellow", "red-blue-yellow")
]


def get_page(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(request)
    return response.read()


def get_game_page(game):
    print("Scraping {0} page...".format(g))
    url = "https://pokemondb.net/pokedex/game/" + game
    soup = BeautifulSoup(get_page(url), "html.parser") 
    return soup


def get_character_cards(page):
    return page.select(".infocard")


def get_character_data(card):
    card_data = card.select_one(".infocard-lg-data")

    gameDexIdStr = card_data.select_one("small").get_text().replace("#", "0").lstrip("0")
    gameDexId = 0

    if gameDexIdStr != "":
        gameDexId = int(gameDexIdStr)

    name = card_data.select_one(".ent-name").get_text()

    return CharacterData(gameDexId, name)


def update_character(data):
    c = db.characters.find_one({ "name": data.name, "altForm": "" })

    if not (c is None):
        gameIndex = -1

        for i, g in enumerate(c["games"]):
            if(g["gameId"] == data.gameId):
                gameIndex = i
                break

        if(gameIndex >= 0):
            db.characters.update_one(
                { "_id": c["_id"] }, 
                { "$set": { "games.{0}.gameDexId".format(gameIndex): data.gameDexId }})


tot = len(game_pages)
ctr = 0

for g in game_pages:
    g_page = get_game_page(g.pageId)
    g_cards = get_character_cards(g_page)

    for c in g_cards:
        data = get_character_data(c)
        data.gameId = g.gameId

        update_character(data)

    ctr += 1
    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))