import collections
import re

from pymongo import MongoClient

def get_nameId(name):
    return name.replace(':', '')\
        .replace(' ', '-')\
        .replace(u'\u2642', '-m')\
        .replace(u'\u2640', '-f')\
        .replace('.', '')\
        .replace(u'\u00E9', 'e')\
        .lower()


client = MongoClient(host='localhost', port=27017)
db = client.pokedex
characters = db.characters.find({ 'altForm': '' })

tot = characters.count()
ctr = 0

for c in characters:
    nameId = get_nameId(c['name'])
    update = { '$set': { 'nameId': nameId } }

    for i, gm in enumerate(c['games']):
        update['$set']['games.{0}.moves'.format(i)] = []


    db.characters.update_one({ '_id': c['_id'] }, update)

    ctr += 1
    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))
        