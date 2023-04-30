from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.cache import Cache, cache_decorator, expired, prepare_key


def test_prepare_key():
    # Проверяем, что функция возвращает строку
    assert isinstance(prepare_key(print), str)

    # Проверяем, что ключи функции правильно сериализуются в строку
    assert (
        prepare_key(sum, [1, 2, 3], start=10)
        == '{"callable": "sum", "args": [[1, 2, 3]], "kwargs": [["start", 10]]}'
    )
    assert (
        prepare_key(lambda x: x, 1, b=2)
        == '{"callable": "<lambda>", "args": [1], "kwargs": [["b", 2]]}'
    )
    assert (
        prepare_key(str.upper, "hello")
        == '{"callable": "upper", "args": ["hello"], "kwargs": []}'
    )


def test_expired():
    with patch('services.cache.datetime') as mocked_datetime:
        # Set the current datetime to a fixed value
        mocked_datetime.now.return_value = datetime(2023, 4, 28, 12, 0, 0)

        # Create a timestamp that is older than the expiration time
        old_timestamp = datetime(2023, 4, 28, 11, 50, 0)

        # Assert that the function returns True for the old timestamp
        assert expired(old_timestamp) == True

        # Create a timestamp that is within the expiration time
        recent_timestamp = datetime(2023, 4, 28, 11, 59, 59)

        # Assert that the function returns False for the recent timestamp
        assert expired(recent_timestamp) == False


@pytest.fixture
def cache_storage() -> Cache:
    return MagicMock(spec=Cache)


@pytest.fixture
def func() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_cache_decorator_returns_cached_value(cache_storage, func):
    key = prepare_key(func, 1, 2, a=3, b=4)
    cache_storage.get.return_value = {
        'timestamp': datetime.now(),
        'response': 'cached_response',
    }

    result = await cache_decorator(cache_storage)(func)(1, 2, a=3, b=4)

    cache_storage.get.assert_called_once_with(key)
    func.assert_not_called()
    assert result == 'cached_response'


@pytest.mark.asyncio
async def test_cache_decorator_calls_decorated_function_and_caches_response(
    cache_storage, func
):
    key = prepare_key(func, 1, 2, a=3, b=4)
    cache_storage.get.return_value = None
    func.return_value = 'new_response'

    result = await cache_decorator(cache_storage)(func)(1, 2, a=3, b=4)

    cache_storage.get.assert_called_once_with(key)
    func.assert_called_once_with(1, 2, a=3, b=4)
    cache_storage.set.assert_called_once()
    assert result == 'new_response'


@pytest.mark.asyncio
async def test_cache_decorator_raises_exception_if_cached_value_has_expired(
    cache_storage, func
):
    key = prepare_key(func, 1, 2, a=3, b=4)
    cache_storage.get.return_value = {
        'timestamp': datetime.now() - timedelta(hours=1),
        'response': 'cached_response',
    }
    func.return_value = 'new_response'

    result = await cache_decorator(cache_storage)(func)(1, 2, a=3, b=4)

    cache_storage.get.assert_called_once_with(key)
    func.assert_called_once_with(1, 2, a=3, b=4)
    cache_storage.set.assert_called_once()
    assert result == 'new_response'
