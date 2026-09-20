from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake


class Move(BaseModel):
    # Auto-generates snake_case aliases (moveId -> move_id, etc.) so
    # model_dump(by_alias=True) lines up with csv_exporter's registered header,
    # matching Character/Dex/Dlc/Game's convention. populate_by_name keeps the
    # camelCase field names usable for construction.
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

    name: str
    nameId: str
    type: str
    category: str
    power: str
    accuracy: str
    pp: str
    effect: str
    probability: str
    # Assigned by MoveBuilder after scraping (sequential across the whole
    # scrape), matching Character/GameCharacter/DlcCharacter's characterId
    # convention - left at 0 until then.
    moveId: int = 0

    def __init__(self, *args, **data) -> None:
        # pydantic's generated __init__ only accepts keyword arguments - this
        # keeps the existing Move(name, nameId, type, category, power,
        # accuracy, pp, effect, probability) positional-call convention
        # working. See Game.__init__/Dlc.__init__ for why positional args are
        # mapped onto field names first rather than bound as named
        # parameters: it lets alias-keyed construction (e.g. model_validate
        # with "name_id" keys) still reach the real pydantic __init__
        # untouched.
        for fieldName, value in zip(
            ('name', 'nameId', 'type', 'category', 'power', 'accuracy', 'pp', 'effect', 'probability'), args
        ):
            data.setdefault(fieldName, value)
        super().__init__(**data)

    def toCsvString(self):
        return "{0},\"{1}\",{2},{3},{4},{5},{6},{7},\"{8}\",{9}\n".format(
            self.moveId, self.name, self.nameId, self.type, self.category,
            self.power, self.accuracy, self.pp, self.effect, self.probability,
        )
