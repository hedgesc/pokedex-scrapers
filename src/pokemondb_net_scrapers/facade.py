"""Public API for the pokemondb.net scraper.

These functions are the package surface. Page parsers stay in the pipeline
packages. HTTP fetching lives in the sibling ``scraping_shared`` package so
another site scraper can use it without importing this package.
"""

from pokemondb_net_scrapers.characters_pipeline import (
    CharacterMovesScraper,
    CharacterScraper,
    NationalDexScraper,
)
from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.dexes_pipeline import DexScraper
from pokemondb_net_scrapers.models.character import Character
from pokemondb_net_scrapers.models.character_seed import CharacterSeed
from pokemondb_net_scrapers.models.dex_character import DexCharacter
from pokemondb_net_scrapers.models.game_character_move import GameCharacterMove
from pokemondb_net_scrapers.models.move import Move
from pokemondb_net_scrapers.moves_pipeline import AllMovesScraper


def list_seed_characters() -> list[CharacterSeed]:
    return NationalDexScraper(settings.national_dex_url).list_seed_characters()


def build_character(seed: CharacterSeed) -> Character:
    return CharacterScraper(settings.character_dex_url(seed.nameId)).build_character(seed)


def list_moves() -> list[Move]:
    return AllMovesScraper(settings.all_moves_url).list_moves()


def list_dex_characters(dex_id: str) -> list[DexCharacter]:
    return DexScraper(settings.game_dex_url(dex_id)).list_dex_characters(dex_id)


def build_character_moves(seed: CharacterSeed) -> list[GameCharacterMove]:
    url = "{0}/moves/{1}".format(settings.character_dex_url(seed.nameId), settings.current_gen)
    return CharacterMovesScraper(url).build_character_moves(seed)
