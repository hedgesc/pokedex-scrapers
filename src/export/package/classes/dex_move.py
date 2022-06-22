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
        self.learnedById = id

        # "Lv.", "HM", "TM"
        if abbr == "Lv.":
            self.learnedBy = "level up"
        elif abbr == "HM":
            self.learnedBy = "hidden machine"
        elif abbr == "TM":
            self.learnedBy = "technical machine"
        else:
            self.learnedBy = 'other'
