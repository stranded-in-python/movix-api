from datetime import datetime, timedelta
from functools import wraps
from json import dumps
from typing import Any, Callable

from core.config import settings
from db.redis import Cache


def expired(timestamp: datetime) -> bool:
    delta = timedelta(seconds=settings.cache_expiration_in_seconds)
    if datetime.now() - timestamp >= delta:
        return True

    return False


def prepare_key(func: Callable, *args, **kwargs) -> str:
    key = {'func': str(type(func)), 'args': args, 'kwargs': sorted(kwargs.items())}
    return dumps(key)


def cache(func, cache_storage: Cache) -> Callable:
    @wraps(func)
    async def inner(*args, **kwargs):
        key = prepare_key(func, *args, **kwargs)
        cached_response = await cache_storage.get(key)
        response = cached_response.get('response')
        if expired(cached_response.get('timestamp')):
            response = await func(*args, **kwargs)
            state = {'timestamp': datetime.now(), 'response': response}
            await cache_storage.set(key, state)
        if not response:
            raise Exception

        return response

    return inner
