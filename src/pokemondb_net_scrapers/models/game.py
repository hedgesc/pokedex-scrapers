class Game:
  def __init__(self, gameId, dexId, name, nameId, regions):
    self.gameId = gameId
    self.dexId = dexId
    self.name = name
    self.nameId = nameId
    self.regions = regions

  def isInDex(self, dexId):
    return self.dexId == dexId

  def toCsvString(self):
    _regions = ','.join(self.regions)
    return "{0},{1},\"{2}\",{3},\"{{{4}}}\"\n".format(self.gameId, self.dexId, self.name, self.nameId, _regions)