def selectImage(card):
	img = card.select_one(".infocard-lg-img > a > .img-sprite")

	if img.has_attr("src"):
		return img.attrs["src"]

	if img.has_attr("data-src"):
		return img.attrs["data-src"]

	return ""

def selectPokemonId(card):
	return card.select_one(".infocard-lg-data > small").get_text().replace("#", "")

def selectName(card):
	return card.select_one(".ent-name").get_text()

def selectTypes(card):
	types = []

	for t in card.select('.itype'):
		types.append(t.get_text())

	return types