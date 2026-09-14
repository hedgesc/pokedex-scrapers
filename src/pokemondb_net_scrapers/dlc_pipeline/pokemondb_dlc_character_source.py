from pokemondb_net_scrapers.dlc_pipeline._pokemondb_html import DlcDexPage
from pokemondb_net_scrapers.models.dlc_character import DlcCharacter
from pokemondb_net_scrapers.utils import parsing


class PokemonDbDlcCharacterSource:
    """DlcCharacterSource backed by pokemondb.net's per-dlc dex listing page
    (settings.dlc_dex_url(dexNameId, dlc.nameId)), analogous to
    PokemonDbGameCharacterSource for games.
    """

    def list_dlc_characters(self, url: str) -> list[DlcCharacter]:
        page = DlcDexPage(url)
        result = []

        for c in page.select_infocards():
            dlc_character = DlcCharacter()
            dlc_character.nameId = parsing.convertToId(c.select_name())
            dlc_character.thumbnailImage = c.select_image()
            dlc_character.pokemonId = c.select_pokemon_id()
            result.append(dlc_character)

        return result
