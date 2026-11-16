from pokemondb_net_scrapers.models.dlc import Dlc
from pokemondb_net_scrapers.static import repo


class StaticYamlDlcSource:
    """DlcSource backed by the hand-maintained static/data/dlcs.yaml.

    All YAML loading/parsing/validation (duplicate ids, dangling dexId
    references, etc.) already lives in static/data.py and static/schema.py -
    this class just adapts that existing data to the DlcSource shape rather
    than re-reading the file itself.
    """

    def list_dlcs(self) -> list[Dlc]:
        return repo.listDlcs()
