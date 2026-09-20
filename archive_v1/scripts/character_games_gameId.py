import collections
import re

from pymongo import MongoClient

class CharacterGame:
    def __init__(self, dexId, name):
        self.gameDexId = dexId
        self.name = name
        

client = MongoClient(host="localhost", port=27017)
db = client.pokedex
results = db.characters.find({ "altForm": "" })

tot = results.count()
ctr = 0

#fname = r['name'].replace(':', '').replace(' ', '-').replace(u'\u2642', '-m').replace(u'\u2640', '-f').replace('.', '').replace(u'\u00E9', 'e').lower()

for r in results:
    
    id_filter = { "_id": r["_id"] }
    games_update = { "$unset": { }, "$set": { } }
    updates = 0

    for i, gm in enumerate(r["games"]):
        
        if "name" not in gm.keys():
            continue

        name = gm["name"].replace("/", "-").replace(" ", "").replace("'", "").lower()

        result = name.find(chr(8212))

        if result != -1:
            name = name[0:result]

        # remove name fields
        set_key = "games.{0}.gameId".format(i)
        set_val = name
        unset_key = "games.{0}.name".format(i)
        
        games_update["$set"][set_key] = set_val
        games_update["$unset"][unset_key] = ""

        updates += 1

    if updates > 0:
        print(games_update)
        db.characters.update(id_filter, games_update)

    ctr += 1
    print("{0}/{1} - {2}".format(ctr, tot, r["name"]))