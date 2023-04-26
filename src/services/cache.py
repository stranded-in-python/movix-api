from datetime import datetime, timedelta
from typing import Any, Callable
from urllib.parse import quote_plus

from fastapi import Request

from core.config import settings
from db.redis import Cache


def expired(cached: dict[str, Any]) -> bool:
    timestamp = cached.get('timestamp')

    if not timestamp:
        raise Exception

    delta = timedelta(seconds=settings.cache_expiration_in_seconds)
    if datetime.now() - timestamp >= delta:
        return True

    return False


def prepare_url_query(request: Request) -> str:
    url = request.url.path + "?"
    for param, value in request.query_params.items():
        if not url.endswith("?"):
            url = url + "&"
        url = f"{url}{param}={quote_plus(value)}"
    return url


def cache(func) -> Callable:
    async def inner(*args, request: Request, **kwargs):
        url_query = prepare_url_query(request)
        cached_response = await Cache.get(url_query)
        response = cached_response.get('response')
        if expired(cached_response):
            response = await func(*args, **kwargs)
            Cache.set(url_query, response)

        if not response:
            raise Exception

        return response

    return inner
