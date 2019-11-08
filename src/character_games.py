import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import collections

def scrape_character_page(name):
    url = 'https://pokemondb.net/pokedex/' + name
    print(url)

client = MongoClient(host='localhost', port=27017)
db = client.pokedex
results = db.characters.find({ 'altForm': '' })

for r in results:
    scrape_character_page(r['name'].lower())

#poop