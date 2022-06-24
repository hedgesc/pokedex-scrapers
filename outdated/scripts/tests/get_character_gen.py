import urllib.request
from bs4 import BeautifulSoup

base_detail_url = "https://pokemondb.net/pokedex/"

name_ids = [
  "bulbasaur",
  "chikorita",
  "treecko",
  "turtwig",
  "victini",
  "chespin",
  "rowlet",
  "grookey"
]

gens = [
  1, 2, 3, 4, 5, 6, 7, 8
]

def get_page(url):
  request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  response = urllib.request.urlopen(request)
  return response.read()

def build_scraper(url):
  page = BeautifulSoup(get_page(url), "html.parser")
  return page

def get_character_gen(url):
  gen = None
  is_gen_list = False
  scraper = build_scraper(url)
  unordered_lists = scraper.select('ul')
  for ul in unordered_lists:
    line_items = ul.select('li')
    for li in line_items:
      if li.get_text().lower() == 'in other generations':
        is_gen_list = True
        break
    if is_gen_list:
      gen = line_items[1].find('a').get_text()
      break
  
  if gen is None:
    return 8
    
  return int(gen)

def equals_test(expected, actual):
  return 'PASS' if expected == actual else 'FAIL'

i = 0
for nameId in name_ids:
  expected = gens[i]
  url = base_detail_url + nameId
  actual = get_character_gen(url)
  status = equals_test(expected, actual)
  print('{0}, {1} = {2}: {3}'.format(nameId, expected, actual, status))
  i += 1


