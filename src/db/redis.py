from typing import Any, Optional

from redis.asyncio import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis  # type: ignore


class Cache:
    def __init__(self, redis):
        self.redis: Redis = redis

    async def get(self, key: str):
        return self.redis.get(key)

    async def set(self, key: str, value: dict[str, Any]):
        await self.redis.set(key, value)  # type: ignore


cache: Optional[Cache] = None
