from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_snake

from pokemondb_net_scrapers.models.game_move import GameMove
from pokemondb_net_scrapers.utils import parsing


class GameCharacterMove(BaseModel):
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

    characterId: int
    dexName: str
    dexNameId: str
    generation: int
    moveName: str
    moveNameId: str
    power: str
    accuracy: str
    learnedBy: str = ""
    learnedById: str = ""
    gameCharacterMoveId: int = 0
    dexId: int = 0
    moveId: int = 0
    isSuggested: bool = False

    def __init__(self, *args, **data) -> None:
        # The fourth positional argument is a GameMove, not a stored field.
        # It is expanded into move columns before validation.
        for field_name, value in zip(("characterId", "dexName", "generation", "game_move"), args):
            data.setdefault(field_name, value)
        super().__init__(**data)

    @model_validator(mode="before")
    @classmethod
    def _expand_game_move(cls, data):
        if not isinstance(data, dict):
            return data

        game_move = data.pop("game_move", None)
        if isinstance(game_move, GameMove):
            data.setdefault("moveName", game_move.moveName)
            data.setdefault("moveNameId", game_move.moveNameId)
            data.setdefault("power", game_move.power)
            data.setdefault("accuracy", game_move.accuracy)
            data.setdefault("learnedBy", game_move.learnedBy)
            data.setdefault("learnedById", game_move.learnedById)

        dex_name = data.get("dexName", data.get("dex_name"))
        if dex_name and "dexNameId" not in data and "dex_name_id" not in data:
            data["dexNameId"] = parsing.convertToDexNameId(dex_name)

        return data

    def getIsSuggested(self) -> str:
        return "t" if self.isSuggested else "f"

    def toCsvString(self) -> str:
        return "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(
            self.gameCharacterMoveId,
            self.dexId,
            self.characterId,
            self.moveId,
            self.generation,
            self.getIsSuggested(),
            self.power,
            self.accuracy,
            self.learnedBy,
            self.learnedById,
        )
