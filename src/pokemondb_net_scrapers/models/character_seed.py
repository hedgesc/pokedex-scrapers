from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_snake

from pokemondb_net_scrapers.utils import parsing


class CharacterSeed(BaseModel):
    """A national-dex listing row, before the species detail page is scraped."""

    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

    name: str
    nameId: str = ""
    characterId: int = 0
    pokemonId: str = ""
    generation: int = 0
    thumbnailUrl: str = ""
    types: list[str] = Field(default_factory=list)

    def __init__(self, *args, **data) -> None:
        for field_name, value in zip(("name",), args):
            data.setdefault(field_name, value)
        super().__init__(**data)

    @model_validator(mode="before")
    @classmethod
    def _default_name_id(cls, data):
        if not isinstance(data, dict):
            return data

        name = data.get("name")
        if name and "nameId" not in data and "name_id" not in data:
            data["nameId"] = parsing.convertToId(name)

        return data
