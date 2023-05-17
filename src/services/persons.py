from functools import lru_cache
from uuid import UUID

from elasticsearch import NotFoundError

from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import PersonShort

from .cache import cache_decorator


class PersonService:
    async def get_by_id(self, person_id: UUID) -> PersonShort | None:
        """Данные по персоне."""
        return await self._get_person_from_elastic(person_id)

    async def get_by_query(
        self, name: str, pagination_params
    ) -> list[PersonShort]:
        """Поиск по персонам."""
        return await self._get_persons_from_elastic(name, pagination_params)

    @cache_decorator(get_cache())
    async def _get_person_from_elastic(self, person_id: UUID) -> PersonShort | None:
        try:
            doc = await get_elastic_manager().get(index='persons', id=person_id)

        except NotFoundError:
            return None

        return PersonShort(**doc.body['_source'])

    @cache_decorator(get_cache())
    async def _get_persons_from_elastic(
        self, name: str, pagination_params
    ) -> list[PersonShort]:
        query = {"match": {"full_name": name}}
        source = ["id", "full_name"]

        try:
            doc = await get_elastic_manager().search(
                index="persons",
                query=query,
                source=source,
                from_=pagination_params.page_number,
                size=pagination_params.page_size,
            )

        except NotFoundError:
            return []

        return list(PersonShort(**hit["_source"]) for hit in doc["hits"]["hits"])


@lru_cache
def get_persons_service() -> PersonService:
    return PersonService()
