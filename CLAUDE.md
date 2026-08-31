# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Scrapes Pokémon/game/move data from pokemondb.net and writes it out as a set of relational CSV files (dexes, games, characters, dlcs, moves, and their join tables) under `src/data/`.

## Commands

Install (editable, with dev/test deps):
```
pip install -e ".[dev]"
```

Run the full scrape (writes CSVs into `src/data/`). **Must be run with `src/` as the working directory** — `config.py`'s `csv_output_folder` is a relative path (`data\`) resolved against the process cwd, not the script location:
```
cd src
python run.py
```

Run tests:
```
python -m pytest
python -m pytest tests/test_config.py           # single file
python -m pytest tests/test_config.py::test_default_base_url   # single test
```
`pyproject.toml` sets `testpaths = ["tests"]` and `pythonpath = ["src"]`, so pytest can locate the package even without the editable install, but prefer the editable install for normal development.

## Architecture

`src/pokemondb_net_scrapers/` is the package (src-layout, installed via `pyproject.toml`'s `[tool.setuptools.packages.find]`). `src/run.py` is the executable entry point/orchestrator — it is a plain top-to-bottom script (no `if __name__ == "__main__"` guard, no CLI framework).

**Execution order in `run.py` is load-bearing.** It builds up module-level lists (`characters`, `games`, `dexes`, `dlcs`, `moves`) sequentially and each later export step looks up rows from the in-memory lists built by earlier steps (e.g. `exportGamesCharacters` needs `dexes` and `characters` already populated; `exportDexesCharactersMoves` needs `dexes`, `characters`, and `moves`). Don't reorder the calls in the `# main` section without tracing these dependencies.

Package layout:
- **`config.py`** — a `pydantic_settings.BaseSettings` class (`Settings`), exported as a singleton `settings`. Holds the base URL, current generation, and every output CSV filename. Fields are overridable via env vars with a `POKEMONDB_` prefix or a `.env` file. Derived pokemondb.net URLs (`base_dex_url`, `national_dex_url`, `all_moves_url`) are `computed_field` properties built from `base_url`, not stored fields.
- **`models/`** — plain data classes for each CSV row type (`Character`, `Dex`, `Game`, `Dlc`, `Move`, `DexCharacter`, `DlcCharacter`, `CharacterDexMove`, `DexMove`). Each has a `toCsvString()` method that formats itself as a CSV row (quoting fields with commas, JSON-array-style `{...}` for list columns like `types`/`abilities`); some also have a `getUrl()` for building their pokemondb.net detail page URL. IDs are assigned by the orchestration code in `run.py`/`scraping/*`, not by the models themselves.
- **`scraping/`** — one top-level module per CSV export (`characters.py`, `games_characters.py`, `dlcs_characters.py`, `moves.py`, `dexes_characters_moves.py`) that orchestrates a scrape (loop over pages/tabs, build model instances). These delegate the actual HTML parsing to `scraping/pages/` — one module per pokemondb.net page type (`national.py` for the national dex listing, `dex.py` for a per-game dex, `dlc.py` for a DLC dex, `character.py` for a character's detail/moves tabs, `move/all.py` for the all-moves table). `scraping/shared/infocard.py` holds BeautifulSoup selectors shared by the several page types that render pokemondb.net's "infocard" grid (used by `national.py`, `dex.py`, `dlc.py`).
- **`static/data.py`** — hardcoded reference lists (`dexes`, `games`, `dlcs`) with their pokemondb.net `nameId` slugs and IDs. This data isn't scraped because pokemondb.net doesn't expose a clean enumerable list of games/dexes/DLCs; **new games/dexes/DLCs must be added here by hand**. `static/repo.py` is a thin accessor layer over it (`listDexes`, `listGames`, `listDlcs`, `listDexGames`).
- **`utils/web.py`** — `getHtml(url)` (fetches via `urllib.request` with a spoofed User-Agent) and `getHtmlParser(markup)` (wraps in BeautifulSoup). All page-fetching goes through this.
- **`utils/parsing.py`** — `convertToId`/`convertToDexNameId` normalize display names (e.g. `"Mr. Mime"`, `"Nidoran♀"`) into the slug format pokemondb.net uses in its URLs.

**Style note:** most of the package (models, scraping) predates `config.py` and uses camelCase for methods/attributes/functions (`toCsvString`, `getUrl`, `scrapeAllCharacters`). `config.py` and its `Settings` fields use snake_case, following `pydantic_settings` convention. Match whichever convention the surrounding file already uses rather than mixing them.

`old/` contains a pre-refactor, unmaintained version of the scraper (flat scripts, no package structure) kept for reference only — it is not part of the current package and should not be imported from or updated.
