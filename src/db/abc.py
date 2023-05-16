from abc import ABC, abstractmethod
from typing import Any

from elastic_transport import ObjectApiResponse

from core.utils import Singleton


class Client(ABC):
    @abstractmethod
    async def close(self):
        ...


class Manager(metaclass=Singleton):
    def __init__(self, client: Client):
        self._client = client

    @classmethod
    def get_instance(cls: type['Manager']):
        return cls._instances.get(cls)

    async def on_shutdown(self):
        await self._client.close()

    @abstractmethod
    async def on_startup(self):
        ...

    def get_client(self) -> Client:
        return self._client


class ElasticManagerABC(Manager):
    @abstractmethod
    async def get(self, *args, **kwargs) -> ObjectApiResponse[Any]:
        ...

    @abstractmethod
    async def search(self, *args, **kwargs) -> ObjectApiResponse[Any]:
        ...
