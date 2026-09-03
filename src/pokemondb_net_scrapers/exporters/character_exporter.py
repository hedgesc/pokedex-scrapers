import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

from ..config import CharacterExportConfig, StorageConfig
from ..interfaces import StorageClient
from ..models import Character

logger = logging.getLogger(__name__)

class CharacterExporter:
    def __init__(
        self,
        characters: dict[str, Character],
        storage_client: StorageClient,
        export_config: CharacterExportConfig,
        storage_config: StorageConfig,
    ) -> None:
        self._characters = characters
        self._storage = storage_client
        self._export_cfg = export_config
        self._storage_cfg = storage_config

    def run(self, character_ids: list[str] | None = None) -> str:
        """Export, upload. Returns the uploaded file's URI."""
        if character_ids is None:
            characters = list(self._characters.values())
        else:
            characters = [self._characters[cid] for cid in character_ids]
        csv_path = self._export_to_csv(characters)
        return self._upload(csv_path)

    def _export_to_csv(self, characters: list[Character]) -> Path:
        cfg = self._export_cfg
        cfg.output_dir.mkdir(parents=True, exist_ok=True)

        filename = cfg.filename_template.format(
            timestamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        )
        path = cfg.output_dir / filename

        rows = [c.model_dump() for c in characters]
        fieldnames = cfg.columns or (list(rows[0].keys()) if rows else [])

        with path.open("w", newline="", encoding=cfg.encoding) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        return path

    def _upload(self, csv_path: Path) -> str:
        cfg = self._storage_cfg
        remote_path = cfg.remote_filename_template.format(
            prefix=cfg.prefix, filename=csv_path.name
        )
        return self._storage.upload_file(str(csv_path), remote_path)