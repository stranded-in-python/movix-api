import codecs
import json
import pickle
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable

from core.config import settings
from db.redis import Cache


def expired(timestamp: datetime) -> bool:
    delta = timedelta(seconds=settings.cache_expiration_in_seconds)
    if datetime.now() - timestamp >= delta:
        return True

    return False


def is_serializable(thing: Any) -> bool:
    try:
        json.dumps(thing)
    except TypeError:
        return False
    return True


def prepare_key(func: Callable, *args, **kwargs) -> str:
    key = {'callable': func.__name__, 'args': args, 'kwargs': sorted(kwargs.items())}
    serialized = ""
    try:
        serialized = json.dumps(key)
    except TypeError:
        # if can't encode straight to json, we need to encode to base64 first
        if not is_serializable(key['args']):
            key['args'] = codecs.encode(pickle.dumps(key['args']), 'base64').decode()
        if not is_serializable(key['kwargs']):
            key['kwargs'] = codecs.encode(
                pickle.dumps(key['kwargs']), 'base64'
            ).decode()
    serialized = json.dumps(key)
    return serialized


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
