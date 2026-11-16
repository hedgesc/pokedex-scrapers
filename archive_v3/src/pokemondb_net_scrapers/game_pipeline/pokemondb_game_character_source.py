from pokemondb_net_scrapers.game_pipeline._pokemondb_html import GameDexPage
from pokemondb_net_scrapers.models.game_character import GameCharacter
from pokemondb_net_scrapers.utils import parsing


class PokemonDbGameCharacterSource:
    """GameCharacterSource backed by pokemondb.net's per-game dex listing
    page (the Dex.getUrl() for the game's dexId), analogous to
    PokemonDbCharacterSource for characters.
    """

    def list_game_characters(self, url: str) -> list[GameCharacter]:
        page = GameDexPage(url)
        result = []

        for c in page.select_infocards():
            game_character = GameCharacter()
            game_character.nameId = parsing.convertToId(c.select_name())
            game_character.thumbnailUrl = c.select_image()
            game_character.pokemonId = c.select_pokemon_id()
            result.append(game_character)

        return result