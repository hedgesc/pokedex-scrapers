from pokemondb_net_scrapers.config import Settings


def test_default_base_url():
	settings = Settings()
	assert settings.base_url == "https://pokemondb.net/"


def test_computed_urls_derive_from_base_url():
	settings = Settings(base_url="https://example.com/")
	assert settings.base_dex_url == "https://example.com/pokedex/"
	assert settings.national_dex_url == "https://example.com/pokedex/national"
	assert settings.all_moves_url == "https://example.com/move/all"
