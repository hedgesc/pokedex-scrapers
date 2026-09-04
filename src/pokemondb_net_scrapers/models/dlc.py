from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake

from ..config import settings

class Dlc(BaseModel):
  # Auto-generates snake_case aliases (dlcId -> dlc_id, etc.) so
  # model_dump(by_alias=True) lines up with csv_exporter's registered header.
  # populate_by_name keeps the camelCase field names usable for construction.
  model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

  dlcId: int
  dexId: int
  name: str
  nameId: str

  def __init__(self, *args, **data) -> None:
    # pydantic's generated __init__ only accepts keyword arguments - this
    # keeps the existing Dlc(dlcId, dexId, name, nameId) positional-call
    # convention working. Every field here is required with no default,
    # so positional args are mapped onto field names first, then
    # everything goes through **data so alias-keyed construction (e.g.
    # Dlc.model_validate({"dlc_id": ...})) still reaches the real
    # pydantic __init__ untouched.
    for fieldName, value in zip(('dlcId', 'dexId', 'name', 'nameId'), args):
      data.setdefault(fieldName, value)
    super().__init__(**data)

  def toCsvString(self):
    return "{0},{1},\"{2}\",{3}\n".format(self.dlcId, self.dexId, self.name, self.nameId)

  def getUrl(self, dexNameId):
    return "{0}game/{1}/{2}".format(settings.base_dex_url, dexNameId, self.nameId)
