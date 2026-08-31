from ..config import settings

class Dex:
  def __init__(self, dexId, nameId, name, alternateName, gen):
    self.dexId = dexId
    self.nameId = nameId
    self.name = name
    self.alternateName = alternateName
    self.gen = gen

  def toCsvString(self):
    return "{0},{1},\"{2}\",\"{3}\",{4}\n".format(self.dexId, self.nameId, self.name, self.alternateName, self.gen)

  def getUrl(self):
    return settings.base_dex_url + "game/" + self.nameId