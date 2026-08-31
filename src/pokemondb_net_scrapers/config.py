"""Configuration settings for the pokemondb_net_scrapers package."""

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_prefix="POKEMONDB_", env_file=".env", extra="ignore")

	base_url: str = "https://pokemondb.net/"
	current_gen: int = 8

	csv_output_folder: str = "data\\"
	characters_csv_file: str = "characters.csv"
	dexes_csv_file: str = "dexes.csv"
	games_csv_file: str = "games.csv"
	games_characters_csv_file: str = "games_characters.csv"
	dlcs_csv_file: str = "dlcs.csv"
	dlcs_characters_csv_file: str = "dlcs_characters.csv"
	moves_csv_file: str = "moves.csv"
	dexes_characters_moves_csv_file: str = "dexes_characters_moves.csv"

	@computed_field
	@property
	def base_dex_url(self) -> str:
		return self.base_url + "pokedex/"

	@computed_field
	@property
	def national_dex_url(self) -> str:
		return self.base_url + "pokedex/national"

	@computed_field
	@property
	def all_moves_url(self) -> str:
		return self.base_url + "move/all"


settings = Settings()
