def convertToId(name):
  return name.replace(":", "")\
    .replace(" ", "-")\
    .replace(u'\u2642', '-m')\
    .replace(u'\u2640', '-f')\
    .replace(".", "")\
    .replace(u'\u00E9', 'e')\
    .replace("'", "")\
    .replace(",", "")\
    .lower()

def convertToDexNameId(name):
  name = name.replace("'", "")

  letsgo = "Lets Go "
  two = " 2"

  if two in name:
    name = name.replace(two, "")
    name = name + two

  if letsgo in name:
    name = name.replace(letsgo, "")
    name = "lets-go-" + name

  return name\
    .replace(":", "")\
    .replace(" ", "-")\
    .replace("/", "-")\
    .lower()