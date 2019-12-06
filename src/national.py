import urllib.request
import collections
import re

from bs4 import Tag, NavigableString, BeautifulSoup
from pymongo import MongoClient

def get_page(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(request)
    return response.read()

def get_national_page():
    url = 'https://pokemondb.net/pokedex/national'
    soup = BeautifulSoup(get_page(url), "html.parser") 
    return soup


def parse_national_page(page):
    for i in range(1, 8):
        print('generation {0}'.format(i))
        print()

        gen_id = '#gen-{0}'.format(i)     
        gen_header = page.select_one(gen_id) 

        for s in gen_header.next_siblings:
            if isinstance(s, NavigableString):
                continue

            if isinstance(s, Tag):
                cards = s.select('.infocard')
                
                tot = len(cards)
                ctr = 0

                for c in cards:
                    data = c.select_one(".infocard-lg-data > small")
    
                    if data is None:
                        continue

                    dexNumber = int(data.get_text().replace("#", "0").lstrip("0"))

                    db.characters.find_one_and_update(
                        { 'dexNumber': dexNumber, 'altForm': '' },
                        { '$set': { 'generation': int(i) } }, 
                        upsert=False)

                    ctr += 1
                    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))

                break

        print()


client = MongoClient(host='localhost', port=27017)
db = client.pokedex

page = get_national_page()
parse_national_page(page)

#tot = len(cards)
ctr = 0



'''
for c in cards:
    data = c.select_one(".infocard-lg-data > small")
    
    if data is None:
        continue

    img = c.select_one(".img-sprite")

    if img is None:
        continue

    dexNumber = int(data.get_text().replace("#", "0").lstrip("0"))
    imageUrl = img.attrs["data-src"]

    print("{0} - {1}".format(dexNumber, imageUrl))

    db.characters.update({'dexNumber': dexNumber, 'altForm': ''}, { '$set': {'imageUrl': imageUrl}})
    
    ctr += 1
    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))

'''