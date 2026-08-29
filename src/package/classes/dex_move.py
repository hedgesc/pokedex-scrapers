from package.utils import util

class DexMove:
    learnedBy = ''
    learnedById = ''

    def __init__(self, moveName, moveNameId, power, accuracy):
        self.moveName = moveName
        self.moveNameId = moveNameId
        self.power = power
        self.accuracy = accuracy

    def setLearnedByInfo(self, abbr, id):
        # "Lv.", "HM", "TM"
        self.learnedBy = abbr
        self.learnedById = id
        