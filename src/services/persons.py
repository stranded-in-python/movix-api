from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Person, PersonShort

PERSON_CACHE_EXPIRE_IN_SECONDS = 24 * 60 * 60  # 24 hours


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: UUID | str) -> PersonShort | None:
        """Данные по персоне."""
        person = await self._person_from_cache(person_id)

        if not person:
            person = await self._get_person_from_elastic(person_id)

            if not person:
                return None

            await self._put_person_to_cache(person)

        return person

    async def get_by_query(
        self, name: str, page_size: int | None, page_number: int | None
    ) -> list[Person]:
        """Поиск по персонам."""
        return await self._get_persons_from_elastic(name, page_size, page_number)

    async def _get_person_from_elastic(self, person_id: UUID | str) -> Person | None:
        try:
            doc = await self.elastic.get(index='persons', id=str(person_id))

        except NotFoundError:
            return None

        return PersonShort(**doc['_source'])

    async def _get_persons_from_elastic(
        self, name: str, page_size: int | None, page_number: int | None
    ):
        query_text = {"match": {"full_name": {"query": name}}}
        body = {
            "from": page_number,
            "size": page_size,
            "query": query_text,
            "_source": ["id", "full_name", "roles", "films"],
        }

        try:
            doc = await self.elastic.search(index="persons", searches=body)

        except NotFoundError:
            return None

        return list(Person(**hit)["_source"] for hit in doc["hits"]["hits"])

    async def _person_from_cache(self, person_id: str) -> Person | None:
        ...

    async def _put_person_to_cache(self, person: Person) -> None:
        ...


@lru_cache
def get_persons_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
