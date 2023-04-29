import logging
import pickle
from typing import Any, Optional, cast

from redis.asyncio import Redis

from core.config import settings
from core.utils import Singleton

from .abc import Client, Manager

redis: Optional[Redis] = None


class RedisClient(Redis, Client):
    """
    Обёртка для redis
    """

    ...


class RedisManager(Manager):
    """
    Singleton для обертки соединения к Redis
    """

    def __init__(self, client: RedisClient):
        super().__init__(client)
        self._client: RedisClient

    def get_client(self) -> RedisClient:
        return self._client

    async def on_startup(self):
        await self._client.ping()


def get_manager() -> RedisManager:
    """
    Метод для получения инстанса менеджера
    """

    manager: Manager | None = cast(RedisManager, RedisManager.get())
    if manager is None:
        manager = RedisManager(
            RedisClient(host=settings.redis_host, port=settings.redis_port)
        )
    return manager


class CacheError(Exception):
    """
    Базовая ошибка кэширования
    """

    ...


class Cache(metaclass=Singleton):
    """
    Класс-обёртка над redis для работы с cache методов.
    """

    def __init__(self, storage: Redis):
        self.redis: Redis = storage

    async def get(self, key: str) -> Any:
        """
        Получить значение из cache по ключу key с отметкой о том, когда было положено
        """
        serialized = await self.redis.get(key)
        value = None
        try:
            if not isinstance(serialized, (bytes, bytearray, memoryview)):
                raise TypeError(f"Failed to deserialize value for key {key}")
            value = pickle.loads(serialized)
        except TypeError or pickle.PicklingError as e:
            logging.error(e)
        return value

    async def set(self, key: str, value: Any):
        """
        Положить значение в cache
        """
        try:
            state = pickle.dumps(value)
        except pickle.UnpicklingError as e:
            logging.error(e)
            raise CacheError("Failed to set an object")
        await self.redis.set(key, state)


def get_cache() -> Cache:
    """
    Получить инстанс Cache
    """
    redis_manager = get_manager()
    storage = redis_manager.get_client()
    return Cache(storage)
