import pokemondb_net_scrapers as scrapers
from pokemondb_net_scrapers.models.character_seed import CharacterSeed


def test_facade_functions_are_the_package_surface():
    assert scrapers.__all__ == [
        "build_character",
        "build_character_moves",
        "list_dex_characters",
        "list_moves",
        "list_seed_characters",
    ]


def test_list_seed_characters_uses_the_national_dex_url(monkeypatch):
    seen = {}

    def fake_list(self):
        seen["url"] = self._page
        return [CharacterSeed("Bulbasaur")]

    monkeypatch.setattr(
        "pokemondb_net_scrapers.characters_pipeline.national_dex_scraper.NationalDexPage",
        lambda url: url,
    )
    monkeypatch.setattr(
        "pokemondb_net_scrapers.characters_pipeline.national_dex_scraper.NationalDexScraper.list_seed_characters",
        fake_list,
    )

    seeds = scrapers.list_seed_characters()

    assert seeds[0].name == "Bulbasaur"
    assert seen["url"].endswith("pokedex/national")
