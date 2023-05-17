from abc import ABC, abstractmethod
from typing import Any

from elastic_transport import ObjectApiResponse

from core.utils import Singleton


class StorageClient(ABC):
    @abstractmethod
    async def close(self):
        ...


class StorageManager(metaclass=Singleton):
    def __init__(self, client: StorageClient):
        self._client = client

    @classmethod
    def get_instance(cls: type['StorageManager']):
        return cls._instances.get(cls)

    async def on_shutdown(self):
        await self._client.close()

    @abstractmethod
    async def on_startup(self):
        ...

    def get_client(self) -> StorageClient:
        return self._client


class ElasticManagerABC(StorageManager):
    @abstractmethod
    async def get(self, *args, **kwargs) -> ObjectApiResponse[Any]:
        ...

    @abstractmethod
    async def search(self, *args, **kwargs) -> ObjectApiResponse[Any]:
        ...
