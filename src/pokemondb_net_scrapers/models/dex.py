from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake

from ..config import settings

class Dex(BaseModel):
  # Auto-generates snake_case aliases (dexId -> dex_id, etc.) so
  # model_dump(by_alias=True) lines up with csv_exporter's registered header.
  # populate_by_name keeps the camelCase field names usable for construction.
  model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

  dexId: int
  nameId: str
  name: str
  alternateName: str
  # to_snake would leave this as "gen" - override to match the header's
  # generation column.
  gen: int = Field(alias='generation')

  def __init__(self, *args, **data) -> None:
    # pydantic's generated __init__ only accepts keyword arguments - this
    # keeps the existing Dex(dexId, nameId, name, alternateName, gen)
    # positional-call convention working. Every field here is required
    # with no default, so positional args are mapped onto field names
    # first, then everything goes through **data so alias-keyed
    # construction (e.g. Dex.model_validate({"dex_id": ...})) still
    # reaches the real pydantic __init__ untouched.
    for fieldName, value in zip(('dexId', 'nameId', 'name', 'alternateName', 'gen'), args):
      data.setdefault(fieldName, value)
    super().__init__(**data)

  def toCsvString(self):
    return "{0},{1},\"{2}\",\"{3}\",{4}\n".format(self.dexId, self.nameId, self.name, self.alternateName, self.gen)

  def getUrl(self):
    return settings.base_dex_url + "game/" + self.nameId
