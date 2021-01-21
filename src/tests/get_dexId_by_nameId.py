import collections
import psycopg2
import psycopg2.extras

connection_string_local = "dbname='pokemondb' user='postgres' host='localhost' password='Super*32'"

name_ids = [
  "red-blue",
  "yellow",
  "gold-silver",
  "crystal",
  "ruby-sapphire",
  "firered-leafgreen",
  "emerald",
  "diamond-pearl",
  "platinum",
  "heartgold-soulsilver",
  "black-white",
  "black-white-2",
  "x-y",
  "omega-ruby-alpha-sapphire",
  "sun-moon",
  "ultra-sun-ultra-moon",
  "lets-go-pikachu-eevee",
  "sword-shield"
]

def get_dexId_by_nameId(nameId):
  sql = """ select dex_id from dexes where name_id = %s """
  conn = None
  dexId = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string_local)
    # create a new cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # execute the sql statement
    cur.execute(sql, (nameId,))
    # get result
    rec = cur.fetchone()
    # close communication with the database
    cur.close()

    if rec is None:
      dexId = None
    
    # return dexId
    dexId = rec[0]
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return None
  finally:
    if conn is not None:
      conn.close()

  return dexId

for nameId in name_ids:
  print('Getting dex_id with {0}'.format(nameId))
  dexId = get_dexId_by_nameId(nameId)
  print('{0}: {1}'.format(nameId, dexId))
  print()