from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake


class DexCharacter(BaseModel):
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

    nameId: str
    pokemonId: str
    thumbnailImage: str
    gameId: int = 0
    characterId: int = 0
    dexId: str = ""

    def __init__(self, *args, **data) -> None:
        for field_name, value in zip(("nameId", "pokemonId", "thumbnailImage"), args):
            data.setdefault(field_name, value)
        super().__init__(**data)

    def toCsvString(self) -> str:
        return "{0},{1},{2},\"{3}\"\n".format(self.gameId, self.characterId, self.pokemonId, self.thumbnailImage)


class GameCharacter(BaseModel):
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

    nameId: str
    pokemonId: str
    thumbnailUrl: str
    gameId: int = 0
    characterId: int = 0

    def __init__(self, *args, **data) -> None:
        for field_name, value in zip(("nameId", "pokemonId", "thumbnailUrl"), args):
            data.setdefault(field_name, value)
        super().__init__(**data)

    def toCsvString(self) -> str:
        return "{0},{1},{2},\"{3}\"\n".format(self.gameId, self.characterId, self.pokemonId, self.thumbnailUrl)
