from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake

class Game(BaseModel):
  # Auto-generates snake_case aliases (gameId -> game_id, etc.) so
  # model_dump(by_alias=True) lines up with csv_exporter's registered header.
  # populate_by_name keeps the camelCase field names usable for construction.
  model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

  gameId: int
  dexId: int
  name: str
  nameId: str
  regions: list[str] = Field(default_factory=list)

  def __init__(self, *args, **data) -> None:
    # pydantic's generated __init__ only accepts keyword arguments - this
    # keeps the existing Game(gameId, dexId, name, nameId, regions)
    # positional-call convention working. Unlike Character, every field here
    # is required with no default, so they can't just be forwarded through
    # **data - positional args are mapped onto field names first, then
    # everything goes through **data so alias-keyed construction (e.g.
    # Game.model_validate({"game_id": ...})) still reaches the real
    # pydantic __init__ untouched.
    for fieldName, value in zip(('gameId', 'dexId', 'name', 'nameId', 'regions'), args):
      data.setdefault(fieldName, value)
    super().__init__(**data)

  def isInDex(self, dexId):
    return self.dexId == dexId

  def toCsvString(self):
    _regions = ','.join(self.regions)
    return "{0},{1},\"{2}\",{3},\"{{{4}}}\"\n".format(self.gameId, self.dexId, self.name, self.nameId, _regions)
