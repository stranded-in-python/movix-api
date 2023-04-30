from abc import ABC, abstractmethod
from typing import Union

from core.utils import Singleton


class Client(ABC):
    @abstractmethod
    async def close(self):
        ...


class Manager(metaclass=Singleton):
    _instance: Union['Manager', None]

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
