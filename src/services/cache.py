from datetime import datetime, timedelta
from typing import Any, Callable

from core.config import Settings
from db. import Cache


def expired(cached: dict[str, Any]) -> bool:
    timestamp = cached.get('timestamp')

    if not timestamp:
        raise Exception

    delta = timedelta(seconds=Settings.API_CACHE_EXPIRES_IN_SECONDS)
    if datetime.now() - timestamp >= delta:
        return True

    return False


def prepare_url_query(*args, **kwargs) -> str:
    return ""


def cache(func) -> Callable:
    async def inner(*args, **kwargs):
        url_query = prepare_url_query(*args, **kwargs)
        cached_response = await Cache.get(url_query)
        response = cached_response.get('response')
        if expired(cached_response):
            response = await func(*args, **kwargs)
            Cache.set(url_query, response)

        if not response:
            raise Exception

        return response

    return inner
