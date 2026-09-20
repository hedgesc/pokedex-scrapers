from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake


class GameCharacter(BaseModel):
    # Auto-generates snake_case aliases (gameId -> game_id, etc.) so
    # model_dump(by_alias=True) lines up with csv_exporter's registered header,
    # matching Character/Game/Dex's convention. populate_by_name keeps the
    # camelCase field names usable for construction.
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)

    nameId: str
    pokemonId: str
    thumbnailUrl: str
    # Resolved after scraping: gameId by whichever game a source scraped this
    # row for, characterId by a cache lookup on nameId. Left at 0 until then,
    # matching the old DexCharacter/DlcCharacter join-row models' convention.
    gameId: int = 0
    characterId: int = 0

    def __init__(self, *args, **data) -> None:
        # pydantic's generated __init__ only accepts keyword arguments - this
        # keeps the old DexCharacter(nameId, pokemonId, thumbnailImage)
        # positional-call convention working. It can't be written as
        # `def __init__(self, nameId, pokemonId, thumbnailUrl, **data)`
        # (like Character does for its single `name` param): when pydantic
        # constructs an instance from alias-keyed data (e.g. model_validate
        # with "name_id"/"pokemon_id"/"thumbnail_url" keys), it calls this
        # __init__ with those same alias keys, which wouldn't bind to
        # differently-named positional parameters. Mapping positional args
        # onto field names first and forwarding everything through **data
        # lets alias-keyed construction reach the real pydantic __init__
        # untouched - see Game.__init__/Dex.__init__ for the same pattern.
        for fieldName, value in zip(('nameId', 'pokemonId', 'thumbnailUrl'), args):
            data.setdefault(fieldName, value)
        super().__init__(**data)

    def toCsvString(self) -> str:
        return "{0},{1},{2},\"{3}\"\n".format(self.gameId, self.characterId, self.pokemonId, self.thumbnailUrl)
