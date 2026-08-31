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

Output CSVs are written to `src/data/`, using a path relative to the working directory, so run from `src/`:

```
cd src
python run.py
```

## Running tests

```
python -m pytest
```

Run a single file or test:

```
python -m pytest tests/test_config.py
python -m pytest tests/test_config.py::test_default_base_url
```
