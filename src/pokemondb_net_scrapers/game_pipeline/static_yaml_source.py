from pokemondb_net_scrapers.models.game import Game
from pokemondb_net_scrapers.static import repo


class StaticYamlGameSource:
    """GameSource backed by the hand-maintained static/data/games.yaml.

    All YAML loading/parsing/validation (duplicate ids, dangling dexId
    references, etc.) already lives in static/data.py and static/schema.py -
    this class just adapts that existing data to the GameSource shape rather
    than re-reading the file itself.
    """

    def list_games(self) -> list[Game]:
        return repo.listGames()
