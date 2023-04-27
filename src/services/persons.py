from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import FilmShort, Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 24 * 60 * 60  # 24 hours


class QueryPerson(BaseModel):
    name: str
    page_size: int | None
    page_number: int | None


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Person | None:
        """Данные по персоне."""
        person = await self._person_from_cache(person_id)

        if not person:
            person = await self._get_person_from_elastic(person_id)

            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_person_films(self, person_id: str) -> list[FilmShort]:
        """Фильмы по персоне."""
        ...  # TODO Посмотреть индекс персон
        # TODO Посмотреть индекс фильмов
        # TODO Написать оптимальный запрос на получение фильмов персоны

    async def get_by_query(self, query: QueryPerson) -> list[Person]:
        """Поиск по персонам."""
        persons = await self._get_persons_from_elastic(query)

        return persons

    async def _get_person_from_elastic(self, person_id: str) -> Person | None:
        try:
            doc = await self.elastic.get('person', person_id)

        except NotFoundError:
            return None

        return Person(**doc['_source'])

    async def _get_person_films_from_elastic(
        self, person_id: str
    ) -> Optional[list[FilmShort]]:
        ...

    async def _get_persons_from_elastic(self, query_param: QueryPerson) -> list[Person]:
        # TODO Нужно ли выводить корутину?
        query_text = {"match": {"full_name": {"query": query_param.name}}}
        body = {
            "from": query_param.page_number,
            "size": query_param.page_size,
            "query": query_text,
            "_source": ["id", "full_name", "roles", "films"],
        }

        try:
            doc = await self.elastic.search(index="persons", body=body)
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
