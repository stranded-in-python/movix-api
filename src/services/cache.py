from datetime import datetime, timedelta
from functools import wraps
from typing import Callable

from core.config import settings
from core.utils import orjson_dumps
from db.redis import Cache


def expired(timestamp: datetime) -> bool:
    delta = timedelta(seconds=settings.cache_expiration_in_seconds)
    if datetime.now() - timestamp >= delta:
        return True

    return False


def prepare_key(func: Callable, *args, **kwargs) -> str:
    key = {
        'callable': func.__name__,
        'args': repr(*args),
        'kwargs': sorted(kwargs.items()),
    }
    return orjson_dumps(key)


def cache_decorator(cache_storage: Cache) -> Callable:
    """
    Декоратор для кэширования результатов вызываемого объекта
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def inner(*args, **kwargs):
            key = prepare_key(func, *args, **kwargs)
            cached_response = await cache_storage.get(key)
            response = cached_response.get('response') if cached_response else None
            if not response or expired(cached_response.get('timestamp')):
                response = await func(*args, **kwargs)
                state = {'timestamp': datetime.now(), 'response': response}
                await cache_storage.set(key, state)
            return response

        return inner

    return decorator
