from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import FilmShort, Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 24 * 60 * 60  # 24 hours


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_person_films(self, person_id: str) -> Optional[list[FilmShort]]:
        ...  # TODO Посмотреть индекс персон
        # TODO Посмотреть индекс фильмов
        # TODO Написать оптимальный запрос на получение фильмов персоны

    async def search(
        self, name: str, page_size: int, page_number: int
    ) -> Optional[Person]:
        persons = await self._get_persons_from_elastic(name, page_size, page_number)

        if not persons:
            return None
        return persons

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get('person', person_id)

        except NotFoundError:
            return None

        return Person(**doc['_source'])

    async def _get_person_films_from_elastic(
        self, person_id: str
    ) -> Optional[list[FilmShort]]:
        ...

    async def _get_persons_from_elastic(
        self, name: str, page_size: int, page_number: int
    ) -> Optional[Person]:
        query = {"match": {"name": {"query": name}}}  # TODO Сверить название со схемой
        body = {
            "from": page_number,
            "size": page_size,
            "query": query,
            "_source": ["id", "full_name", "roles", "films"],
        }

        try:
            doc = await self.elastic.search(index="persons", body=body)
        except NotFoundError:
            return None

        return [Person(**hit)["_source"] for hit in doc["hits"]["hits"]]

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        ...

    async def _put_person_to_cache(self, person: Person) -> None:
        ...


@lru_cache
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
