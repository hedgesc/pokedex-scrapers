from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake

from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.utils import parsing

class Character(BaseModel):
  # Auto-generates snake_case aliases (characterId -> character_id, etc.) so
  # model_dump(by_alias=True) lines up with csv_exporter's registered header.
  # populate_by_name keeps the camelCase field names usable for construction.
  model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

  name: str
  nameId: str = ''
  characterId: int = 0
  pokemonId: str = ''
  total: int = 0
  hp: int = 0
  attack: int = 0
  defense: int = 0
  specialAttack: int = 0
  specialDefense: int = 0
  speed: int = 0
  alternateName: str = ''
  generation: int = 0
  finalEvolutionId: str = ''
  types: list[str] = Field(default_factory=list)
  abilities: list[str] = Field(default_factory=list)
  thumbnailUrl: str = ''
  # to_snake would otherwise produce image_url_1/image_url_2 - override to
  # match the header's image_url1/image_url2 columns.
  imageUrl1: str = Field(default='', alias='image_url1')
  imageUrl2: str = Field(default='', alias='image_url2')
  isVisible: bool = True
  isAlternateForm: bool = False

  def __init__(self, name: str, **data) -> None:
    # nameId is derived from name unless a caller explicitly overrides it -
    # keeps the old Character(name) construction style working.
    data.setdefault('nameId', parsing.convertToId(name))
    super().__init__(name=name, **data)

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