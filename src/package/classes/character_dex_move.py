from package.utils import util

class CharacterDexMove:
    characterDexMoveId = 0
    dexId = 0
    moveId = 0
    isSuggested = False

    def __init__(self, characterId, dexName, generation, dexMove):
        self.characterId = characterId
        self.dexName = dexName
        self.dexNameId = util.convertToDexNameId(dexName)
        self.generation = generation
        self.moveName = dexMove.moveName
        self.moveNameId = dexMove.moveNameId
        self.power = dexMove.power
        self.accuracy = dexMove.accuracy
        self.learnedBy = dexMove.learnedBy
        self.learnedById = dexMove.learnedById

    def getIsSuggested(self):
        return "t" if self.isSuggested else "f"

    def toCsvString(self):
        return "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(self.characterDexMoveId, self.dexId, self.characterId, self.moveId, self.generation, self.getIsSuggested(), self.power, self.accuracy, self.learnedBy, self.learnedById)
