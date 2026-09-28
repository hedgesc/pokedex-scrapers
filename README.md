# pokedex-scrapers
A project containing various Python scripts for scraping pokedex data

## Setup

Requires Python >= 3.14.0.

```
git clone https://github.com/chedges27/pokedex-scrapers.git
cd pokedex-scrapers
pip install -e ".[dev]"
```

## Running the scraper

There is no single full-scrape command — the package is mid-migration from its original `run.py` orchestrator to a set of per-entity pipelines (see `CLAUDE.md`), and `run.py` has been archived to `archive_v2/src/run.py` along with most of the code it drove.

In its place, each pipeline is exported as one background job, meant to be scheduled independently (this project uses [RQ](https://python-rq.org/)) rather than run as one in-process script:

```python
from redis import Redis
from rq import Queue

from pokemondb_net_scrapers.jobs import export_pipeline_to_csv

queue = Queue(connection=Redis())
job = queue.enqueue(export_pipeline_to_csv, "characters")
```

`export_pipeline_to_csv(pipeline_name)` scrapes/loads that pipeline's data, exports it to a local CSV file, and returns the file's path. Only the pipeline name — a plain string — needs to cross the queue; everything else (the `Builder`, the cache client) is constructed inside the worker when the job runs. **Uploading the exported file anywhere is the job scheduler's responsibility, not this package's** — there's deliberately no storage/upload client here.

Currently registered pipeline names: `characters`, `dexes`, `games`, `dlcs`, `moves`, `games_characters`, `dlcs_characters`. (`dexes_characters_moves` doesn't have a pipeline yet, so it isn't an option here.)

**Job ordering is the caller's responsibility, not this package's.** `games_characters` and `dlcs_characters` resolve `characterId`/`dexId` by reading the shared cache the `characters`/`dexes` jobs populate — if a dependent job runs before its dependency has finished, it raises (`CacheKeyNotFoundError` or similar) rather than waiting or guessing. Schedule `characters` and `dexes` before `games_characters`/`dlcs_characters`, and let your job queue's own retry policy handle a job that ran too early.

Configuration (env vars, prefixed `POKEMONDB_`, or a `.env` file — see `config.py`):

| Setting | Purpose | Default |
| --- | --- | --- |
| `POKEMONDB_REDIS_URL` | Backs the shared cache (`RedisCacheClient`) | `redis://localhost:6379/0` |
| `POKEMONDB_CSV_OUTPUT_FOLDER` | Where each job writes its exported CSV | `data\` |

## Running tests

```
python -m pytest
```

Run a single file or test:

```
python -m pytest tests/test_config.py
python -m pytest tests/test_config.py::test_default_base_url
```

## Versioning

The package version is derived from git tags via [hatch-vcs](https://github.com/ofek/hatch-vcs) — there is no version string to bump by hand. To cut a release, tag the commit (`vX.Y.Z`) and push the tag:

```
git tag v0.1.0
git push origin v0.1.0
```

Building from that exact commit produces a wheel/sdist versioned `0.1.0`. Commits after a tag get a dev version (e.g. `0.1.1.dev3+g<sha>`).

To install a specific version in a Docker image, install directly from the git tag:

```dockerfile
RUN pip install "pokedex-scrapers @ git+https://github.com/chedges27/pokedex-scrapers.git@v0.1.0"
```

or build the wheel for that tag first and `COPY` it into the image.
