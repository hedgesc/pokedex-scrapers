"""Configuration settings for the pokemondb_net_scrapers package."""

from pydantic import computed_field, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class ExportConfig(BaseModel):
	output_dir: Path = Path("./exports")
	columns: list[str] | None = None
	encoding: str = "utf-8"


class CharacterExportConfig(ExportConfig):
	filename_template: str = "characters_{timestamp}.csv"


class StorageConfig(BaseModel):
    bucket: str
    prefix: str = "pokedex/exports/"
    remote_filename_template: str = "{prefix}{filename}"
    overwrite: bool = False
    ttl_days: int | None = Field(default=None, description="Optional lifecycle hint, if backend supports it")


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
	def all_moves_url(self) -> str:
		return self.base_url + "move/all"

	@computed_field
	@property
	def national_dex_url(self) -> str:
		return self.base_dex_url + "national"

	def character_dex_url(self, nameId) -> str:
		return self.base_dex_url + nameId


settings = Settings()
