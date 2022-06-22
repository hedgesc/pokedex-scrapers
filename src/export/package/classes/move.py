class Move:
	moveId = 0

	def __init__(self, name, nameId, type, category, power, accuracy, pp, effect, probability):
		self.name = name
		self.nameId = nameId
		self.type = type
		self.category = category
		self.power = power
		self.accuracy = accuracy
		self.pp = pp
		self.effect = effect
		self.probability = probability

	def toCsvString(self):
		return "{0},\"{1}\",{2},{3},{4},{5},{6},{7},\"{8}\",{9}\n".format(self.moveId, self.name, self.nameId, self.type, self.category, self.power, self.accuracy, self.pp, self.effect, self.probability)