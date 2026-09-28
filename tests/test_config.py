from pokemondb_net_scrapers.config import Settings


def test_default_base_url():
	settings = Settings()
	assert settings.base_url == "https://pokemondb.net/"


def test_default_csv_output_folder():
	settings = Settings()
	assert settings.csv_output_folder == "data\\"


def test_csv_output_folder_overridable_via_env_var(monkeypatch):
	monkeypatch.setenv("POKEMONDB_CSV_OUTPUT_FOLDER", "/tmp/pokedex-exports/")

	settings = Settings()

	assert settings.csv_output_folder == "/tmp/pokedex-exports/"


def test_computed_urls_derive_from_base_url():
	settings = Settings(base_url="https://example.com/")
	assert settings.base_dex_url == "https://example.com/pokedex/"
	assert settings.national_dex_url == "https://example.com/pokedex/national"
	assert settings.all_moves_url == "https://example.com/move/all"
