import time
from dataclasses import dataclass


@dataclass
class _Entry:
    value: str
    expires_at: float | None


class InMemoryCacheClient:
    """A CacheClient implementation backed by a plain dict in process memory.

    Not a real cache - nothing here is shared across processes or persisted
    across runs. Meant for local development and tests that need something
    satisfying the CacheClient protocol without standing up a real backend
    (e.g. CharacterBuilder(source, InMemoryCacheClient(), ...)).
    """

    def __init__(self, *, clock=time.monotonic) -> None:
        self._clock = clock
        self._entries: dict[str, _Entry] = {}

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        expires_at = self._clock() + ttl if ttl is not None else None
        self._entries[key] = _Entry(value=value, expires_at=expires_at)

    def get(self, key: str) -> str | None:
        entry = self._entries.get(key)

        if entry is None:
            return None

        if entry.expires_at is not None and self._clock() >= entry.expires_at:
            del self._entries[key]
            return None

        return entry.value

    def clear(self) -> None:
        self._entries.clear()

    def keys(self) -> list[str]:
        """Keys currently live (i.e. not expired), for test assertions."""
        return [k for k in self._entries if self.get(k) is not None]

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __len__(self) -> int:
        return len(self.keys())
