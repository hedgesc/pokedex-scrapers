# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Scrapes Pokémon/game/move data from pokemondb.net and writes it out as a set of relational CSV files (dexes, games, characters, dlcs, moves, and their join tables) under `src/data/`.

## Commands

Install (editable, with dev/test deps):
```
pip install -e ".[dev]"
```

There is currently no working full-scrape entry point — `run.py` was archived (see below) along with most of `scraping/` once the `*_pipeline` packages superseded them, and nothing has wired the new pipelines up to a replacement orchestrator yet. `archive_v2/src/run.py` is the last-working reference for how the full scrape used to be sequenced.

Run tests:
```
python -m pytest
python -m pytest tests/test_config.py           # single file
python -m pytest tests/test_config.py::test_default_base_url   # single test
```
`pyproject.toml` sets `testpaths = ["tests"]` and `pythonpath = ["src"]`, so pytest can locate the package even without the editable install, but prefer the editable install for normal development.

## Architecture

`src/pokemondb_net_scrapers/` is the package (src-layout, installed via `pyproject.toml`'s `[tool.setuptools.packages.find]`).

**This package is mid-migration**, moving from the original flat `run.py` + `scraping/*` orchestration (list-scanning in-memory to resolve cross-entity ids) to a Source/Builder pipeline per entity — `character_pipeline/`, `dex_pipeline/`, `game_pipeline/`, `dlc_pipeline/`, `move_pipeline/` — that resolve ids through a shared `CacheClient` (`interfaces.py`) instead. Once an entity's pipeline exists, its old `scraping/*` module and (if nothing else needs it) its `scraping/pages/*` module get archived to `archive_v2/` — see below. `run.py` itself has been archived too, since it orchestrated across all entities; nothing has replaced it yet, so there is currently no single full-scrape entry point.

Not every entity is migrated yet. `scraping/dexes_characters_moves.py` and `scraping/pages/character.py` are still live — the character↔dex↔move join hasn't been rebuilt as a pipeline. Don't archive or restructure these without checking whether that work has landed; **`models/character_dex_move.py` and `models/dex_move.py` are likewise still load-bearing for it.**

Package layout:
- **`config.py`** — a `pydantic_settings.BaseSettings` class (`Settings`), exported as a singleton `settings`. Holds the base URL, current generation, every output CSV filename, and a `CacheConfig` (per-entity cache key prefixes, TTL, `raise_on_cache_error`) used by the pipelines below. Fields are overridable via env vars with a `POKEMONDB_` prefix or a `.env` file. Derived pokemondb.net URLs (`base_dex_url`, `national_dex_url`, `all_moves_url`, plus per-entity URL builders like `game_dex_url`/`dlc_dex_url`) are `computed_field` properties/methods built from `base_url`, not stored fields.
- **`interfaces.py`** — `Protocol`s the pipelines depend on rather than a concrete implementation: `CacheClient` (`get`/`set`), `ExportableModel`. `caching.RedisCacheClient` is the real `CacheClient`. There's deliberately no upload-side `Protocol`/client here - `jobs.py`'s job functions only scrape and export a local CSV; uploading it is the job scheduler's responsibility, not this package's.
- **`models/`** — one model per CSV row type (`Character`, `Dex`, `Game`, `Dlc`, `Move`, `GameCharacter`, `DlcCharacter`, plus the still-in-use legacy `DexCharacter`, `CharacterDexMove`, `DexMove`). Each has a `toCsvString()` method that formats itself as a CSV row (quoting fields with commas, JSON-array-style `{...}` for list columns like `types`/`abilities`); some also have a `getUrl()`/`getDetailUrl()` for building their pokemondb.net page URL. Most are now `pydantic.BaseModel`s with a `to_snake` alias generator (so `model_dump(by_alias=True)` lines up with `csv_exporter`'s registered header) and a custom `__init__` that keeps the old positional-constructor calling convention working. IDs are assigned by whichever orchestration code builds the model — the old `scraping/*`/`run.py`, or a `*_pipeline` `Builder` now.
- **`character_pipeline/`, `dex_pipeline/`, `game_pipeline/`, `dlc_pipeline/`, `move_pipeline/`** — the new pipelines. Each has a `Source` protocol (`source.py`) plus a concrete implementation — `pokemondb_source.py` (HTML-backed, via a private `_pokemondb_html.py`) and/or `static_yaml_source.py` (backed by `static/data/*.yaml` via `static/repo.py`) — and a `Builder` (`builder.py`) that assigns ids and resolves any cross-entity references through the shared cache. A join between two entities (e.g. `GameCharacter`) nests inside whichever pipeline owns the *iteration root* — the entity whose per-item page is fetched to discover the other side — as a fully-named trio (`game_character_source.py`, `pokemondb_game_character_source.py`, `game_character_builder.py`) alongside the package's own unprefixed `source.py`/`builder.py`. `shared/infocard_html.py` holds the `InfocardTag` selector reused by `character_pipeline`, `game_pipeline`, and `dlc_pipeline` — cross-pipeline reuse always goes through `shared/`, never through another pipeline's underscore-prefixed `_pokemondb_html.py`. `testing/InMemoryCacheClient` is a `CacheClient` test double for local dev/tests.
- **`scraping/`** — what's left of the pre-pipeline orchestration: `dexes_characters_moves.py` (still live, not yet migrated) plus `pages/character.py` (also still live — it's shared between the archived character-detail scraping and the still-live moves scraping) and the package-marker `__init__.py`s. Everything else that used to be here (`characters.py`, `games_characters.py`, `dlcs_characters.py`, `moves.py`, `pages/dex.py`, `pages/dlc.py`, `pages/national.py`, `pages/move/`, `shared/`) has been archived to `archive_v2/` now that its `*_pipeline` replacement exists.
- **`jobs.py`** — `export_pipeline_to_csv(pipeline_name)`, the interface a background job (RQ) calls: `queue.enqueue(export_pipeline_to_csv, "characters")`. Only the plain pipeline-name string crosses the queue; a `name -> Builder-factory` registry (`jobs._BUILDERS`) constructs everything else (`Source`, `CacheClient`) inside the worker when the job runs. Cross-pipeline job ordering (e.g. `characters` before `games_characters`) is the caller's scheduler's responsibility, not this module's - a cross-entity cache miss propagates uncaught rather than being retried here.
- **`caching/`** — `RedisCacheClient`, the real `CacheClient` backing the pipelines' shared cache now that each one can run as its own job/process rather than a step of one script.
- **`static/data.py`** — hardcoded reference lists (`dexes`, `games`, `dlcs`) with their pokemondb.net `nameId` slugs and IDs. This data isn't scraped because pokemondb.net doesn't expose a clean enumerable list of games/dexes/DLCs; **new games/dexes/DLCs must be added here by hand**. `static/repo.py` is a thin accessor layer over it (`listDexes`, `listGames`, `listDlcs`, `listDexGames`), used by both the old `run.py` path and the new pipelines' `static_yaml_source.py` implementations.
- **`utils/web.py`** — `getHtml(url)` (fetches via `urllib.request` with a spoofed User-Agent) and `getHtmlParser(markup)` (wraps in BeautifulSoup). All page-fetching goes through this.
- **`utils/parsing.py`** — `convertToId`/`convertToDexNameId` normalize display names (e.g. `"Mr. Mime"`, `"Nidoran♀"`) into the slug format pokemondb.net uses in its URLs.

**Style note:** most of the package predates `config.py` and uses camelCase for methods/attributes/functions (`toCsvString`, `getUrl`, `scrapeAllCharacters`); model *fields* on the pydantic models are camelCase too, with snake_case only as the generated alias. `config.py`, `interfaces.py`, and the `*_pipeline` packages use snake_case for methods/functions, following `pydantic_settings`/PEP 8 convention. Match whichever convention the surrounding file already uses rather than mixing them.

`archive_v1/` contains a pre-refactor, unmaintained version of the scraper (flat scripts, no package structure) kept for reference only. `archive_v2/` contains the package-structured `run.py` + `scraping/*` code that the `*_pipeline` packages have since superseded, kept for reference while the remaining not-yet-migrated pieces (the character↔dex↔move join) still exist. Neither is part of the current package and neither should be imported from or updated.
