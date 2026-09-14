from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake


class DlcCharacter(BaseModel):
    # Auto-generates snake_case aliases (dlcId -> dlc_id, etc.) so
    # model_dump(by_alias=True) lines up with csv_exporter's registered header,
    # matching Character/Game/Dex/GameCharacter's convention. populate_by_name
    # keeps the camelCase field names usable for construction.
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

    nameId: str
    pokemonId: str
    thumbnailImage: str
    # Resolved after scraping: dlcId by whichever dlc a source scraped this
    # row for, characterId by a cache lookup on nameId. Left at 0 until then,
    # matching GameCharacter's convention.
    dlcId: int = 0
    characterId: int = 0

    def __init__(self, *args, **data) -> None:
        # pydantic's generated __init__ only accepts keyword arguments - this
        # keeps the existing DlcCharacter(nameId, pokemonId, thumbnailImage)
        # positional-call convention working. See GameCharacter.__init__ for
        # why positional args are mapped onto field names first rather than
        # bound as named parameters: it lets alias-keyed construction (e.g.
        # model_validate with "name_id"/"pokemon_id" keys) still reach the
        # real pydantic __init__ untouched.
        for fieldName, value in zip(('nameId', 'pokemonId', 'thumbnailImage'), args):
            data.setdefault(fieldName, value)
        super().__init__(**data)

    def toCsvString(self) -> str:
        return "{0},{1},{2},\"{3}\"\n".format(self.dlcId, self.characterId, self.pokemonId, self.thumbnailImage)
