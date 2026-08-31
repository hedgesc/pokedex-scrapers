from ..config import settings

class Dlc:
	def __init__(self, dlcId, dexId, name, nameId):
		self.dlcId = dlcId
		self.dexId = dexId
		self.name = name
		self.nameId = nameId

	def toCsvString(self):
		return "{0},{1},\"{2}\",{3}\n".format(self.dlcId, self.dexId, self.name, self.nameId)

	def getUrl(self, dexNameId):
		return "{0}game/{1}/{2}".format(settings.base_dex_url, dexNameId, self.nameId)