from functools import lru_cache
from uuid import UUID

from elasticsearch import NotFoundError

from db.elastic import ElasticManager
from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import Person, PersonShort

from .cache import cache_decorator

PERSON_CACHE_EXPIRE_IN_SECONDS = 24 * 60 * 60  # 24 hours


class PersonService:
    def __init__(self, elastic: ElasticManager):
        self.elastic: ElasticManager = elastic

    async def get_by_id(self, person_id: UUID) -> PersonShort | None:
        """Данные по персоне."""
        return await self._get_person_from_elastic(person_id)

    async def get_by_query(
        self, name: str, page_size: int | None = None, page_number: int | None = None
    ) -> list[PersonShort]:
        """Поиск по персонам."""
        return await self._get_persons_from_elastic(name, page_size, page_number)

    @cache_decorator(get_cache())
    async def _get_person_from_elastic(self, person_id: UUID) -> Person | None:
        try:
            doc = await self.elastic.get(index='persons', id=person_id)

        except NotFoundError:
            return None

        return PersonShort(**doc.body['_source'])

    @cache_decorator(get_cache())
    async def _get_persons_from_elastic(
        self, name: str, page_size: int | None = None, page_number: int | None = None
    ) -> list[PersonShort]:
        query = {"match": {"full_name": name}}
        source = ["id", "full_name"]

        try:
            doc = await self.elastic.search(
                index="persons",
                query=query,
                source=source,
                from_=page_number,
                size=page_size,
            )

        except NotFoundError:
            return None

        return list(PersonShort(**hit["_source"]) for hit in doc["hits"]["hits"])


@lru_cache
def get_persons_service() -> PersonService:
    return PersonService(get_elastic_manager())
