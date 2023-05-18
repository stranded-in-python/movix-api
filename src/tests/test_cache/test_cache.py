from unittest.mock import AsyncMock

import fakeredis
import pytest

from cache.cache import Cache
from db.redis import RedisClient

pytestmark = pytest.mark.asyncio


@pytest.fixture
def redis_client():
    redis = fakeredis.FakeStrictRedis()
    client = AsyncMock(spec=RedisClient)
    client.get = AsyncMock(wraps=redis.get)
    client.set = AsyncMock(wraps=redis.set)
    client.ping = AsyncMock()
    return client


@pytest.fixture
def cache(redis_client):
    return Cache(redis_client)


async def test_get_cache(cache):
    key = "my_key"
    value = {"my_value": 42}
    await cache.set(key, value)
    result = await cache.get(key)
    assert result == value
