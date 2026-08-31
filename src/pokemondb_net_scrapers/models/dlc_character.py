class DlcCharacter:
	dlcId = 0
	characterId = 0

	def __init__(self, nameId, pokemonId, thumbnailImage):
		self.nameId = nameId
		self.pokemonId = pokemonId
		self.thumbnailImage = thumbnailImage

	def toCsvString(self):
		return "{0},{1},{2},\"{3}\"\n".format(self.dlcId, self.characterId, self.pokemonId, self.thumbnailImage)
