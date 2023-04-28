from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis
import pytest

from db.redis import Cache, RedisClient, RedisManager, get_manager


@pytest.fixture
def redis_client():
    redis = fakeredis.FakeStrictRedis()
    client = MagicMock(spec=RedisClient)
    client.get = AsyncMock(wraps=redis.get)
    client.set = AsyncMock(wraps=redis.set)
    client.ping = AsyncMock()
    return client


@pytest.fixture
def redis_manager(redis_client):
    manager = RedisManager(redis_client)
    manager.on_startup = AsyncMock()
    manager.on_shutdown = AsyncMock()
    return manager


@pytest.mark.asyncio
async def test_redis_client_ping(redis_client):
    await redis_client.ping()
    redis_client.ping.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_manager_returns_instance(redis_manager):
    with patch.object(RedisManager, "get") as mocked_get:
        mocked_get.return_value = redis_manager
        manager = get_manager()
        assert manager == redis_manager


@pytest.mark.asyncio
async def test_get_manager_creates_new_instance(redis_manager, redis_client):
    with (
        patch.object(RedisManager, "get") as mocked_manager_get,
        patch.object(RedisManager, "__new__") as mocked_manager_new,
        patch.object(RedisClient, "__new__") as mocked_client_new,
    ):
        mocked_manager_get.return_value = None
        mocked_manager_new.return_value = redis_manager
        mocked_client_new.return_value = redis_client
        manager = get_manager()
        assert manager == redis_manager


@pytest.fixture
def cache(redis_client):
    return Cache(redis_client)


@pytest.mark.asyncio
async def test_get_cache(cache):
    key = "my_key"
    value = {"my_value": 42}
    await cache.set(key, value)
    result = await cache.get(key)
    assert result == value
