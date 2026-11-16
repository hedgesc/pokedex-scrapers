from typing import Protocol, runtime_checkable

@runtime_checkable
class CacheClient(Protocol):
    """Minimal contract the package needs from any distributed cache."""

    def set(self, key: str, value: str, ttl: int | None = None) -> None: ...
    def get(self, key: str) -> str | None: ...

@runtime_checkable
class ExportableModel(Protocol):
    def toCsvString() -> str:
        """Returns this object as a csv string for export."""
        ...