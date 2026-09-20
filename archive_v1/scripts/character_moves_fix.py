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
characters = db.character_moves.find()

tot = characters.count()
ctr = 0

for c in characters:
    nameId = get_nameId(c['name'])

    g = db.games.find_one({ 'gameId': c['gameId']})
    displayName = g['displayName']

    update = { '$set': { 'nameId': nameId, 'game': displayName } }

    for i, cm in enumerate(c['moves']):
        m = db.moves.find_one({ 'moveId': cm['moveId'] })

        if not ('$unset' in update):
            update['$unset'] = {}

        update['$unset']['moves.{0}.color'.format(i)] = ''
        update['$set']['moves.{0}.type'.format(i)] = m['type']
        update['$set']['moves.{0}.pp'.format(i)] = m['pp']


    db.character_moves.update_one({ '_id': c['_id'] }, update)

    ctr += 1
    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))
        