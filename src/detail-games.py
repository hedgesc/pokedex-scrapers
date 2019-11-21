import urllib.request
import collections
import re

from bs4 import BeautifulSoup
from pymongo import MongoClient

class CharacterGame:
    def __init__(self, dexId, name):
        self.gameDexId = dexId
        self.name = name

def get_page(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(request)
    return response.read()

def scrape_character_page(name):
    url = 'https://pokemondb.net/pokedex/' + name
    soup = BeautifulSoup(get_page(url), "html.parser")
    
    games_cell = soup.select_one('.vitals-table tr:last-child > td')

    if games_cell is None:
        print('{0}: unable to retrieve game data: no results found matching .vitals-table tr:last-child > td'.format(name))
        return
    
    game_data_raw = games_cell.get_text()
    
    if game_data_raw == '—':
        return []

    game_data = list(filter(None, re.split("(\d+\s\(.*?\))", game_data_raw)))
    
    c_games = []

    for g in game_data:
        m = re.match("^(?P<dexId>\d+)\s\((?P<name>.*?)\)$", g)
        g_dexIdStr = m.group('dexId').lstrip('0')
        
        if g_dexIdStr == '':
            g_dexId = 0
        else:
            g_dexId = int(g_dexIdStr)
        
        g_name = m.group('name')
        cg = CharacterGame(g_dexId, g_name)
        c_games.append(cg.__dict__)

    return c_games    
        

client = MongoClient(host='localhost', port=27017)
db = client.pokedex
results = db.characters.find({ 'altForm': '' })

tot = results.count()
ctr = 0

for r in results:
    fname = r['name'].replace(':', '').replace(' ', '-').replace(u'\u2642', '-m').replace(u'\u2640', '-f').replace('.', '').replace(u'\u00E9', 'e').lower()
    games = scrape_character_page(fname)
    db.characters.update_one({'_id': r['_id']}, {'$set': {'games': games}})

    ctr += 1
    print("{0}/{1} - {2}".format(ctr, tot, fname))
