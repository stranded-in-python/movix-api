from typing import cast

from elasticsearch import AsyncElasticsearch

from core.config import settings

from .abc import Client, Manager


class ElasticClient(AsyncElasticsearch, Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ElasticManager(Manager):
    def __init__(self, client: ElasticClient):
        super().__init__(client)
        self._client: ElasticClient

    def get_client(self) -> ElasticClient:
        return self._client

    async def on_startup(self):
        await self._client.ping()


async def get_manager() -> ElasticManager:
    manager: Manager | None = cast(ElasticManager, ElasticManager.get())
    if manager is None:
        manager = ElasticManager(ElasticClient(hosts=[settings.elastic_endpoint]))
    return manager
