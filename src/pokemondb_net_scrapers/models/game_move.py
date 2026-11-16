from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake


class GameMove(BaseModel):
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

    moveName: str
    moveNameId: str
    power: str
    accuracy: str
    learnedBy: str = ""
    learnedById: str = ""

    def __init__(self, *args, **data) -> None:
        for field_name, value in zip(("moveName", "moveNameId", "power", "accuracy"), args):
            data.setdefault(field_name, value)
        super().__init__(**data)

    def setLearnedByInfo(self, abbr: str, learned_id: str) -> None:
        # "Lv.", "HM", "TM"
        self.learnedBy = abbr
        self.learnedById = learned_id
