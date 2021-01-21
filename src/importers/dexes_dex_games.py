import collections
import psycopg2
import psycopg2.extras

connection_string_local = "dbname='pokemondb' user='postgres' host='localhost' password='Super*32'"
connection_string_prod  = "dbname='pokemondb' user='pi' host='10.0.0.42' password='Super*32'"

class Dex:
  def __init__(self, nameId, name, alternateName, gen):
    self.nameId = nameId
    self.name = name
    self.alternateName = alternateName
    self.gen = gen

class Game:
  dexId = None

  def __init__(self, dexNameId, name, nameId, regions):
    self.dexNameId = dexNameId
    self.name = name
    self.nameId = nameId
    self.regions = regions


dexes = [
  Dex("red-blue","Red/Blue","Red & Blue",1),
  Dex("yellow","Yellow","Yellow",1),
  Dex("crystal","Crystal","Crystal",2),
  Dex("gold-silver","Gold/Silver","Gold & Silver",2),
  Dex("firered-leafgreen","FireRed/LeafGreen","FireRed & LeafGreen",3),
  Dex("ruby-sapphire","Ruby/Sapphire","Ruby & Sapphire",3),
  Dex("emerald","Emerald","Emerald",3),
  Dex("diamond-pearl","Diamond/Pearl","Diamon & Pearl",4),
  Dex("platinum","Platinum","Platinum",4),
  Dex("heartgold-soulsilver","HeartGold/SoulSilver","HeartGold & SoulSilver",4),
  Dex("black-white","Black/White","Black & White",5),
  Dex("black-white-2","Black 2/White 2","Black 2 & White 2",5),
  Dex("x-y","X/Y","X & Y",6),
  Dex("omega-ruby-alpha-sapphire","Omega Ruby/Alpha Sapphire","Omega Ruby & Alpha Sapphire",6),
  Dex("sun-moon","Sun/Moon","Sun & Moon",7),
  Dex("ultra-sun-ultra-moon","Ultra Sun/Ultra Moon","Ultra Sun & Ultra Moon",7),
  Dex("lets-go-pikachu-eevee","Let's Go Pikachu/Let's Go Eevee","Let's Go Pikachu & Let's Go Eevee",7),
  Dex("sword-shield","Sword/Shield","Sword & Shield",8)
]

games = [
  Game("red-blue","Red","red",["Kanto"]),
  Game("red-blue","Blue","blue",["Kanto"]),
  Game("yellow","Yellow","yellow",["Kanto"]),
  Game("gold-silver","Gold","gold",["Kanto","Johto"]),
  Game("gold-silver","Silver","silver",["Kanto","Johto"]),
  Game("crystal","Crystal","crystal",["Kanto","Johto"]),
  Game("ruby-sapphire","Ruby","ruby",["Hoenn"]),
  Game("ruby-sapphire","Sapphire","sapphire",["Hoenn"]),
  Game("emerald","Emerald","emerald",["Hoenn"]),
  Game("firered-leafgreen","FireRed","firered",["Kanto"]),
  Game("firered-leafgreen","LeafGreen","leafgreen",["Kanto"]),
  Game("platinum","Platinum","platinum",["Sinnoh"]),
  Game("heartgold-soulsilver","HeartGold","heartgold",["Kanto","Johto","Hoenn","Sinnoh"]),
  Game("heartgold-soulsilver","SoulSilver","soulsilver",["Kanto","Johto","Hoenn","Sinnoh"]),
  Game("diamond-pearl","Pearl","pearl",["Sinnoh"]),
  Game("diamond-pearl","Diamond","diamond",["Sinnoh"]),
  Game("black-white-2","Black 2","black2",["Unova"]),
  Game("black-white-2","White 2","white2",["Unova"]),
  Game("black-white","Black","black",["Unova"]),
  Game("black-white","White","white",["Unova"]),
  Game("omega-ruby-alpha-sapphire","Omega Ruby","omega-ruby",["Hoenn"]),
  Game("omega-ruby-alpha-sapphire","Alpha Sapphire","alpha-sapphire",["Hoenn"]),
  Game("x-y","X","x",["Kalos"]),
  Game("x-y","Y","y",["Kalos"]),
  Game("ultra-sun-ultra-moon","Ultra Sun","ultra-sun",["Alola"]),
  Game("ultra-sun-ultra-moon","Ultra Moon","ultra-moon",["Alola"]),
  Game("lets-go-pikachu-eevee","Let's Go Pikachu","lets-go-pikachu",["Kanto"]),
  Game("lets-go-pikachu-eevee","Let's Go Eevee","lets-go-eevee",["Kanto"]),
  Game("sun-moon","Sun","sun",["Alola"]),
  Game("sun-moon","Moon","moon",["Alola"]),
  Game("sword-shield","Sword","sword",["Galar"]),
  Game("sword-shield","Shield","shield",["Galar"])
]


def find_games_by_dex(nameId):
  return [g for g in games if g.dexNameId == nameId]


def insert_dex(dex):
  sql = """ INSERT INTO dexes(name,name_id,alternate_name,gen)
  VALUES(%(name)s,%(nameId)s,%(alternateName)s,%(gen)s) RETURNING dex_id; """
  
  conn = None
  dexId = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string_local)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, dex.__dict__)
    # get the generated id back
    dexId = cur.fetchone()[0]
    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return None
  finally:
    if conn is not None:
      conn.close()

  return dexId


def insert_game(dexId, game):
  game.dexId = dexId

  sql = """ INSERT INTO dex_games(dex_id,name,name_id,regions)
  VALUES(%(dexId)s,%(name)s,%(nameId)s,%(regions)s) RETURNING game_id; """
  
  conn = None
  gameId = None
  
  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string_local)
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, game.__dict__)
    # get the generated id back
    dexId = cur.fetchone()[0]
    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return None
  finally:
    if conn is not None:
      conn.close()

  return gameId


def execute_sql(sql):
  conn = None

  try:
    # connect to the PostgreSQL database
    conn = psycopg2.connect(connection_string_local)
    # create a new cursor
    cur = conn.cursor()
    # execute the sql statement
    cur.execute(sql)
    # commit
    conn.commit()
    # close communication with the database
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()


print("Truncating dexes, dex_games, dexes_characters")
print()
execute_sql("TRUNCATE dexes RESTART IDENTITY CASCADE;")

print("Importing Dexes")
print()

for dex in dexes:
  print("- Importing {0} pokedex".format(dex.name))
  print()

  dex_id = insert_dex(dex)

  games_list = find_games_by_dex(dex.nameId)

  for g in games_list:
    print("-- Importing game {0}".format(g.name))
    game_id = insert_game(dex_id, g)

  print()