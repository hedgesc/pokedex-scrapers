class Game:
  def __init__(self, gameId, dexId, name, nameId, regions):
    self.gameId = gameId
    self.dexId = dexId
    self.name = name
    self.nameId = nameId
    self.regions = regions

  def isInDex(self, dexId):
    truthy = self.dexId in dexId
    return truthy

  def toCsvString(self):
    _regions = ','.join(self.regions) if len(self.regions) > 1 else self.regions[0]
    return "{0},{1},\"{2}\",{3},\"{{{4}}}\"\n".format(self.gameId, self.dexId, self.name, self.nameId, _regions)