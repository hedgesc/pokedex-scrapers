from typing import Protocol, runtime_checkable

@runtime_checkable
class CacheClient(Protocol):
    """Minimal contract the package needs from any distributed cache."""

    def set(self, key: str, value: str, ttl: int | None = None) -> None: ...
    def get(self, key: str) -> str | None: ...

@runtime_checkable
class StorageClient(Protocol):
    """Minimal contract for uploading a file to cloud storage."""

    def upload_file(self, local_path: str, remote_path: str) -> str:
        """Returns the final URI/URL of the uploaded object."""
        ...

@runtime_checkable
class ExportableModel(Protocol):
    def toCsvString() -> str:
        """Returns this object as a csv string for export."""
        ...