from typing import cast

from elasticsearch import AsyncElasticsearch

from core.config import settings

from .abc import ElasticManagerABC, StorageClient


class ElasticClient(AsyncElasticsearch, StorageClient):
    """Обёртка для ElasticSearch"""

    ...


class ElasticManager(ElasticManagerABC):
    """
    Singleton для управления соединением с elasticsearch
    """

    def __init__(self, client: ElasticClient):
        super().__init__(client)
        self._client: ElasticClient

    def get_client(self) -> ElasticClient:
        return self._client

    async def on_startup(self):
        await self._client.ping()

    async def get(self, *args, **kwargs):
        return await self.get_client().get(*args, **kwargs)

    async def search(self, *args, **kwargs):
        return await self.get_client().search(*args, **kwargs)


def get_manager() -> ElasticManager:
    """
    Получить instance менеджера
    """

    manager: ElasticManager | None = cast(ElasticManager, ElasticManager.get_instance())
    if manager is None:
        manager = ElasticManager(ElasticClient(hosts=[settings.elastic_endpoint]))
    return manager
