import redis

from pokemondb_net_scrapers.config import settings


class RedisCacheClient:
    """CacheClient backed by Redis.

    Jobs run as independent RQ workers now, not steps of one in-process
    script, so the nameId -> id caches CharacterBuilder/DexBuilder/
    MoveBuilder populate (and GameCharacterBuilder/DlcCharacterBuilder read)
    have to be visible across processes for cross-pipeline id resolution to
    work at all - the in-process testing.InMemoryCacheClient can't do that.
    RQ itself already requires a Redis instance, so this reuses that rather
    than introducing a second piece of infrastructure.

    Accepts an already-constructed client for tests (a fake, or a real
    redis.Redis pointed at a test instance) instead of always connecting via
    settings.redis_url.
    """

    def __init__(self, redis_url: str | None = None, client: "redis.Redis | None" = None) -> None:
        self._client = client or redis.Redis.from_url(redis_url or settings.redis_url, decode_responses=True)

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self._client.set(key, value, ex=ttl)

    def get(self, key: str) -> str | None:
        return self._client.get(key)
