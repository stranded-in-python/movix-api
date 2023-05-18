from unittest.mock import AsyncMock

import fakeredis
import pytest

from db.redis import RedisClient, RedisManager, get_manager

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
def redis_manager(redis_client):
    manager = RedisManager(redis_client)
    manager.on_startup = AsyncMock()
    manager.on_shutdown = AsyncMock()
    return manager


async def test_redis_client_ping(redis_client):
    await redis_client.ping()
    redis_client.ping.assert_awaited_once()


async def test_get_manager_returns_instance(mocker, redis_manager):
    mocked_get = mocker.patch.object(RedisManager, "get_instance")
    mocked_get.return_value = redis_manager
    manager = get_manager()
    assert manager == redis_manager
    mocked_get.stop()
