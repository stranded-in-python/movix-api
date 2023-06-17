from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, cast

from elastic_transport import ObjectApiResponse

from core.singleton import Singleton


class DBClient(ABC):
    @abstractmethod
    async def close(self):
        ...


class DBManager(metaclass=Singleton):
    def __init__(self, client: DBClient):
        self._client = client

    @classmethod
    def get_instance(cls: type[DBManager]):
        return cls._instances.get(cls)

    async def on_shutdown(self):
        await self._client.close()

    @abstractmethod
    async def on_startup(self):
        ...

    def get_client(self) -> DBClient:
        return self._client


class ElasticManagerABC(DBManager):
    @abstractmethod
    async def get(self, *args, **kwargs) -> ObjectApiResponse[Any]:
        ...

    @abstractmethod
    async def search(self, *args, **kwargs) -> ObjectApiResponse[Any]:
        ...

    @classmethod
    def get_instance(cls) -> ElasticManagerABC | None:
        instance = super().get_instance()

        if instance is None:
            return

        return cast(ElasticManagerABC, instance)
