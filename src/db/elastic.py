from typing import Any, Mapping, cast

from elasticsearch import AsyncElasticsearch

from core.config import settings

from .abc import Client, Manager


class ElasticClient(AsyncElasticsearch, Client):
    """
    Обёртка для ElasticSearch
    """

    ...


class ElasticManager(Manager):
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

    async def get(self, index: str, id: str):
        return await self._client.get(index=index, id=id)

    async def search(
        self,
        index: str,
        query: dict[str, Any],
        source: bool | Mapping[str, Any] | None = None,
        aggs: dict[str, Any] | None = None,
    ):
        return await self._client.search(
            index=index, query=query, aggs=aggs, source=source
        )


def get_manager() -> ElasticManager:
    """
    Получить instance менеджера
    """

    manager: ElasticManager | None = cast(ElasticManager, ElasticManager.get_instance())
    if manager is None:
        manager = ElasticManager(ElasticClient(hosts=[settings.elastic_endpoint]))
    return manager
