from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from cache.cache import Cache, cache_decorator, prepare_key

pytestmark = pytest.mark.asyncio


@pytest.fixture
def cache_storage() -> Cache:
    return MagicMock(spec=Cache)


@pytest.fixture
def func() -> AsyncMock:
    return AsyncMock()


@pytest.mark.parametrize(
    'args,kwargs,expected',
    [((1, 2), {}, {'timestamp': datetime.now(), 'response': 'cached_response'})],
)
async def test_cache_decorator_returns_cached_value(
    cache_storage, func, args, kwargs, expected
):
    cache_storage.get.return_value = expected
    key = prepare_key(func, *args, **kwargs)
    result = await cache_decorator(cache_storage)(func)(*args, **kwargs)

    cache_storage.get.assert_called_once_with(key)
    func.assert_not_called()
    assert result == expected['response']


@pytest.mark.parametrize(
    'args,kwargs,expected', [((1, 2), {'a': 3, 'b': 4}, 'new_response')]
)
async def test_cache_decorator_calls_decorated_function_and_caches_response(
    cache_storage, func, args, kwargs, expected
):
    key = prepare_key(func, *args, **kwargs)
    cache_storage.get.return_value = None
    func.return_value = expected
    result = await cache_decorator(cache_storage)(func)(*args, **kwargs)

    cache_storage.get.assert_called_once_with(key)
    func.assert_called_once_with(*args, **kwargs)
    cache_storage.set.assert_called_once()
    assert result == expected


@pytest.mark.parametrize(
    'args,kwargs,timestamp,cached_result,new_result,expected',
    [
        (
            (1, 2),
            {'a': 3, 'b': 4},
            datetime.now() - timedelta(hours=1),
            'cached_response',
            'new_response',
            'new_response',
        ),
        (
            (1, 2),
            {'a': 3, 'b': 4},
            datetime.now() - timedelta(minutes=1),
            'cached_response',
            'new_response',
            'cached_response',
        ),
    ],
)
async def test_cache_decorator_raises_exception_if_cached_value_has_expired(
    cache_storage, func, args, kwargs, timestamp, cached_result, new_result, expected
):
    key = prepare_key(func, *args, **kwargs)
    cache_storage.get.return_value = {'timestamp': timestamp, 'response': cached_result}

    func.return_value = new_result
    result = await cache_decorator(cache_storage)(func)(*args, **kwargs)

    cache_storage.get.assert_called_once_with(key)
    assert result == expected
