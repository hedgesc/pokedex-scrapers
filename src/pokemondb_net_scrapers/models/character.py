from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.utils import parsing

class Character:
  def __init__(self):
    self.characterId = 0
    self.pokemonId = ''
    self.name = ''
    self.total = 0
    self.hp = 0
    self.attack = 0
    self.defense = 0
    self.specialAttack = 0
    self.specialDefense = 0
    self.speed = 0
    self.nameId = ''
    self.alternateName = ''
    self.generation = 0
    self.finalEvolutionId = ''
    self.types = []
    self.abilities = []
    self.thumbnailUrl = ''
    self.imageUrl1 = ''
    self.imageUrl2 = ''
    self.isVisible = True
    self.isAlternateForm = False

  def serebiiNetImage(self):
    return "https://www.serebii.net/pokemon/art/{0}.png".format(self.pokemonId)

  def getDetailUrl(self):
    return settings.base_dex_url + self.nameId

  def setBaseStats(self, stats):
    self.hp = stats.hp
    self.attack = stats.attack
    self.defense = stats.defense
    self.specialAttack = stats.specialAttack
    self.specialDefense = stats.specialDefense
    self.speed = stats.speed
    self.total = stats.total

  def getIsVisible(self):
    return "t" if self.isVisible else "f"

  def toCsvString(self):
    _types = ','.join(self.types)
    _abilities = ','.join(self.abilities)

    return "{0},{1},{2},\"{3}\",{4},{5},{6},{7},{8},{9},{10},{11},{12},\"{{{13}}}\",\"{{{14}}}\",{15},{16},\"{17}\",\"{18}\",\"{19}\"\n".format(self.characterId, self.pokemonId, self.generation, self.name, self.total, self.hp, self.attack, self.defense, self.specialAttack, self.specialDefense, self.speed, self.nameId, self.alternateName, _types, _abilities, self.finalEvolutionId, self.getIsVisible(), self.thumbnailUrl, self.imageUrl1, self.imageUrl2)


class BaseStats:
  def __init__(self):
    self.total = None
    self.hp = None
    self.attack = None
    self.defense = None
    self.specialAttack = None
    self.specialDefense = None
    self.speed = None


class CharacterTab:
  def __init__(self, index, tab):
    self.index = index
    self.name = tab.get_text()
    self.panel = tab['href']

  def isAlternateForm(self):
    return self.index > 0


class DexMovesTab:
  def __init__(self, tab):
    self.name = tab.get_text()
    self.panelId = tab["href"]