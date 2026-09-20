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

There is currently no working full-scrape entry point. The package is mid-migration from its original `run.py` orchestrator to a set of per-entity pipelines (see `CLAUDE.md`), and `run.py` has been archived to `archive_v2/src/run.py` along with most of the code it drove — nothing has replaced it yet.

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
