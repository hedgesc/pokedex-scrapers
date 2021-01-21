import psycopg2
import psycopg2.extras
import collections

connection_string_local = "dbname='pokedex' user='postgres' host='localhost' password='Super*32'"
connection_string_prod  = "dbname='pokedex' user='pi' host='10.0.0.42' password='Super*32'"

def get_characters():
  sql = "SELECT * FROM characters ORDER BY character_id"

  conn = None

  try:
    conn = psycopg2.connect(connection_string_prod)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    characters = cur.fetchall()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
  
  return characters


def update_character(id, image_url):
  sql = """ UPDATE characters
            SET image_url = %s
            WHERE character_id = %s"""
  
  conn = None
  updated_rows = 0

  try:
    conn = psycopg2.connect(connection_string_prod)
    cur = conn.cursor()
    cur.execute(sql, (image_url, id))
    updated_rows = cur.rowcount
    conn.commit()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()

  return updated_rows


baseUrl = 'https://www.serebii.net/swordshield/pokemon/'
fileExt = '.png'
characters = get_characters()

tot = len(characters)
ctr = 0

for c in characters:
  image_url = '{0}{1:03d}{2}'.format(baseUrl, c['character_id'], fileExt)
  character_id = c['character_id']

  rows_updated = update_character(character_id, image_url)

  ctr += 1
  print('{0}/{1} {2:.1%} - {3}: {4} row(s) updated'.format(ctr, tot, ctr / tot, character_id, rows_updated))
