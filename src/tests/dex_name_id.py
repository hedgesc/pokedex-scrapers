import collections

names = [
  "Red/Blue",
  "Yellow",
  "Gold/Silver",
  "Crystal",
  "Ruby/Sapphire",
  "FireRed/LeafGreen",
  "Emerald",
  "Diamond/Pearl",
  "Platinum",
  "HeartGold/SoulSilver",
  "Black/White",
  "Black 2/White 2",
  "X/Y",
  "Omega Ruby/Alpha Sapphire",
  "Sun/Moon",
  "Ultra Sun/Ultra Moon",
  "Let's Go Pikachu/Let's Go Eevee",
  "Sword/Shield"
]

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

def equals_test(expected, actual):
  return 'PASS' if expected == actual else 'FAIL'

def get_dex_nameId(name):
  name = name.replace("'", '')

  letsgo = "Lets Go "
  two = " 2"

  if two in name:
    name = name.replace(two, '')
    name = name + two

  if letsgo in name:
    name = name.replace(letsgo, '')
    name = 'lets-go-' + name

  return name\
    .replace(' ', '-')\
    .replace('/', '-')\
    .lower()

i = 0

for name in names:
  expected = name_ids[i]
  actual = get_dex_nameId(name)
  status = equals_test(expected, actual)
  print('{0}, {1} = {2}: {3}'.format(name, expected, actual, status))
  i += 1


