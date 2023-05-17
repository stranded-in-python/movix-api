from collections.abc import Callable
from functools import lru_cache
from uuid import UUID

from elasticsearch import NotFoundError

from db.abc import ElasticManagerABC
from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import PersonShort

from .abc import PersonServiceABC, PersonStorageABC
from .cache import cache_decorator


class PersonElasticStorage(PersonStorageABC):
    def __init__(self, manager: Callable[[], ElasticManagerABC]):
        self.manager = manager

    @cache_decorator(get_cache())
    async def get_item(self, person_id: UUID) -> PersonShort | None:
        try:
            doc = await self.manager().get(index='persons', id=person_id)

        except NotFoundError:
            return None

        return PersonShort(**doc.body['_source'])

    @cache_decorator(get_cache())
    async def get_items(self, filters: str, pagination_params) -> list[PersonShort]:
        query = {"match": {"full_name": filters}}
        source = ["id", "full_name"]

        try:
            doc = await self.manager().search(
                index="persons",
                query=query,
                source=source,
                from_=pagination_params.page_number,
                size=pagination_params.page_size,
            )

        except NotFoundError:
            return []

        return list(PersonShort(**hit["_source"]) for hit in doc["hits"]["hits"])


class PersonService(PersonServiceABC):
    def __init__(self, storage: PersonStorageABC):
        self.storage = storage

    async def get_by_id(self, item_id: UUID) -> PersonShort | None:
        """Данные по персоне."""
        return await self.storage.get_item(item_id)

    async def get_by_query(self, name: str, pagination_params) -> list[PersonShort]:
        """Поиск по персонам."""
        return await self.storage.get_items(name, pagination_params)


@lru_cache
def get_persons_service() -> PersonService:
    return PersonService(storage=PersonElasticStorage(get_elastic_manager))
