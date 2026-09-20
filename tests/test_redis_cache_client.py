from pokemondb_net_scrapers.caching import RedisCacheClient


class FakeRedis:
    """Minimal stand-in for redis.Redis - just enough of .set()/.get() for
    RedisCacheClient to drive, without a real Redis server. Doesn't model
    actual expiry; it only records the ttl it was asked to set."""

    def __init__(self):
        self.values: dict[str, str] = {}
        self.set_calls: list[tuple[str, str, int | None]] = []

    def set(self, name, value, ex=None):
        self.set_calls.append((name, value, ex))
        self.values[name] = value

    def get(self, name):
        return self.values.get(name)


def test_set_stores_value_retrievable_by_get():
    fake = FakeRedis()
    client = RedisCacheClient(client=fake)

    client.set("characters:pikachu", "25")

    assert client.get("characters:pikachu") == "25"


def test_get_returns_none_for_missing_key():
    client = RedisCacheClient(client=FakeRedis())
    assert client.get("characters:missingno") is None


def test_set_passes_ttl_through_as_ex():
    fake = FakeRedis()
    client = RedisCacheClient(client=fake)

    client.set("moves:tackle", "1", ttl=3600)

    assert fake.set_calls == [("moves:tackle", "1", 3600)]


def test_set_defaults_ttl_to_none():
    fake = FakeRedis()
    client = RedisCacheClient(client=fake)

    client.set("moves:tackle", "1")

    assert fake.set_calls == [("moves:tackle", "1", None)]


def test_constructor_builds_a_real_redis_client_from_url_when_none_given():
    client = RedisCacheClient(redis_url="redis://example.invalid:6379/0")

    # Connecting is lazy in redis-py - constructing the client shouldn't
    # itself require a reachable server. Just confirm it built something
    # that looks like a real client, distinct from an injected fake.
    assert type(client._client).__name__ == "Redis"
