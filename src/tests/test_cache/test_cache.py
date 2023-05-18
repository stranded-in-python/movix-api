from datetime import datetime
from unittest.mock import AsyncMock

import fakeredis
import pytest

from cache.cache import Cache, expired, prepare_key
from db.redis import RedisClient


@pytest.mark.parametrize(
    'args,kwargs,expected',
    [
        (
            [sum, [1, 2, 3]],
            {'start': 10},
            '{"callable": "sum", "args": [[1, 2, 3]], "kwargs": [["start", 10]]}',
        ),
        (
            [lambda x: x, 1],
            {'b': 2},
            '{"callable": "<lambda>", "args": [1], "kwargs": [["b", 2]]}',
        ),
        (
            [str.upper, "hello"],
            {},
            '{"callable": "upper", "args": ["hello"], "kwargs": []}',
        ),
    ],
)
def test_prepare_key(args, kwargs, expected):
    # Проверяем, что функция возвращает строку
    assert isinstance(prepare_key(print), str)

    # Проверяем, что ключи функции правильно сериализуются в строку
    assert prepare_key(*args, **kwargs) == expected


@pytest.mark.parametrize(
    'now, expired_time, recent_time',
    [
        (
            datetime(2023, 4, 28, 12, 0, 0),
            datetime(2023, 4, 28, 11, 50, 0),
            datetime(2023, 4, 28, 11, 59, 59),
        )
    ],
)
def test_expired(mocker, now, expired_time, recent_time):
    mocked_datetime = mocker.patch('cache.cache.datetime')
    # Set the current datetime to a fixed value
    mocked_datetime.now.return_value = now

    # Assert that the function returns True for the old timestamp
    assert expired(expired_time) == True

    # Assert that the function returns False for the recent timestamp
    assert expired(recent_time) == False


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


@pytest.mark.parametrize('key,value', [('my_key', {'my_value': 42})])
@pytest.mark.asyncio
async def test_get_cache(cache, key, value):
    await cache.set(key, value)
    result = await cache.get(key)
    assert result == value
