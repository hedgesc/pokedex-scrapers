from pokemondb_net_scrapers.models.dex import Dex
from pokemondb_net_scrapers.static import repo


class StaticYamlDexSource:
    """DexSource backed by the hand-maintained static/data/dexes.yaml.

    All YAML loading/parsing/validation (duplicate ids/nameIds, etc.) already
    lives in static/data.py and static/schema.py - this class just adapts
    that existing data to the DexSource shape rather than re-reading the
    file itself.
    """

    def list_dexes(self) -> list[Dex]:
        return repo.listDexes()
