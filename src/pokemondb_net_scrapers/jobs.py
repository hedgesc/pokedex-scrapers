"""The scrape/export entry point RQ jobs call.

    queue.enqueue(export_pipeline_to_csv, "characters")

Job ordering across pipelines (e.g. running "characters" before
"games_characters", which needs its cache entries) is owned by whatever
schedules these jobs, not this module - a cross-entity cache miss
(CacheKeyNotFoundError, DexNotFoundError, ...) is left to propagate so the
scheduler's own retry policy can re-run the job once its dependency has
landed, rather than this module guessing at a wait/backoff of its own.

Only a plain pipeline-name string crosses the queue: RQ pickles a reference
to export_pipeline_to_csv plus its arguments, and a live Builder/CacheClient
isn't something that survives that - each one is constructed fresh inside
the worker process, when the job actually runs.

Uploading the exported file (if at all) is the job scheduler's job, not
this module's - export_pipeline_to_csv only writes the local CSV and
returns its path; there is deliberately no StorageClient/upload step here.
"""

from .caching import RedisCacheClient
from .character_pipeline import CharacterBuilder, PokemonDbCharacterSource
from .dex_pipeline import DexBuilder, StaticYamlDexSource
from .dlc_pipeline import DlcBuilder, DlcCharacterBuilder, PokemonDbDlcCharacterSource, StaticYamlDlcSource
from .game_pipeline import GameBuilder, GameCharacterBuilder, PokemonDbGameCharacterSource, StaticYamlGameSource
from .interfaces import CacheClient
from .move_pipeline import MoveBuilder, PokemonDbMoveSource
from .services import csv_exporter


def get_cache_client() -> CacheClient:
    return RedisCacheClient()


def _characters():
    return CharacterBuilder(PokemonDbCharacterSource(), get_cache_client())


def _dexes():
    return DexBuilder(StaticYamlDexSource(), get_cache_client())


def _games():
    # No cache dependency of its own - games.yaml fully describes each Game,
    # so there's nothing here for another job to have populated first.
    return GameBuilder(StaticYamlGameSource())


def _dlcs():
    return DlcBuilder(StaticYamlDlcSource())


def _moves():
    return MoveBuilder(PokemonDbMoveSource(), get_cache_client())


def _games_characters():
    # games.yaml is loaded fresh here rather than depending on the "games"
    # job's output - it's cheap, local, and not itself scraped, so there's
    # no ordering concern in loading it again. The real cross-job
    # dependencies are the characters/dexes caches GameCharacterBuilder
    # reads, populated by the "characters"/"dexes" jobs.
    games = StaticYamlGameSource().list_games()
    return GameCharacterBuilder(PokemonDbGameCharacterSource(), games, get_cache_client())


def _dlcs_characters():
    dlcs = StaticYamlDlcSource().list_dlcs()
    return DlcCharacterBuilder(PokemonDbDlcCharacterSource(), dlcs, get_cache_client())


# pipeline name -> zero-arg factory returning that pipeline's Builder.
# Adding a pipeline is one entry here; export_pipeline_to_csv itself never
# needs to change.
_BUILDERS = {
    "characters": _characters,
    "dexes": _dexes,
    "games": _games,
    "dlcs": _dlcs,
    "moves": _moves,
    "games_characters": _games_characters,
    "dlcs_characters": _dlcs_characters,
}


def export_pipeline_to_csv(pipeline_name: str) -> str:
    """Scrape/load pipeline_name's data, export it to a local CSV file, and
    return the file's path.

    Raises KeyError for an unregistered pipeline_name. Any error the
    underlying Builder raises (a cross-entity cache miss included) is left
    to propagate uncaught - see the module docstring.
    """
    if pipeline_name not in _BUILDERS:
        raise KeyError("Unknown pipeline '{0}'. Known pipelines: {1}".format(pipeline_name, sorted(_BUILDERS)))

    builder = _BUILDERS[pipeline_name]()
    items = builder.build()

    return csv_exporter.export(items)
