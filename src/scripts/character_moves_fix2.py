import collections
import re

from pymongo import MongoClient


client = MongoClient(host='localhost', port=27017)
db = client.pokedex
c_moves = db.character_moves.find()


def get_game(gameId):
    return db.games.find_one({ 'gameId': gameId })


def get_character(nameId, gameId):
    return db.characters.aggregate([
        { '$unwind': '$games' },
        { '$match' : { 'nameId': nameId, 'games.gameId': gameId } },
        { '$sort'  : { 'dexNumber': 1 } }
    ])


tot = c_moves.count()
ctr = 0

for cm in c_moves:
    
    cursor = get_character(cm['nameId'], cm['gameId'])
    _c = None

    try:
        _c = cursor.next()
    except StopIteration:
        continue

    _g = get_game(cm['gameId'])

    update = { '$set': { 'charIndex': _c['games']['gameDexId'], 'gameIndex': _g['order'] } }

    db.character_moves.update_one({ '_id': cm['_id'] }, update)

    ctr += 1
    print("{0}/{1} {2:.1%}".format(ctr, tot, ctr / tot))
        