from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmShort

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    # Serge пока(?) без редис
    async def get_films(self, sort: str,
                        page_size: int,
                        page_number: int,
                        genre_name: str) -> Optional[FilmShort]:
        films = await self._get_films_from_elastic(sort, page_size, page_number, genre_name)
        if not films:
            return None
        return films

    async def _get_films_from_elastic(
            self, sort: str, page_number: int, page_size: int, genre_name=None
            ) -> Optional[FilmShort]:
        try:
            if genre_name:
                query = {
                        "bool": {
                        "filter": [{"terms": { "genre" : [genre_name]}}]} # ! пока что genre_name. Должен быть id
                        }
            else:
                query = {"match_all": {}}
            body = {
                    "from": page_number, "size": page_size, "query": query,
                    "_source": ["id", "imdb_rating", "title"]
                    }
            doc = await self.elastic.search(index="movies",body=body, sort=f"{sort}:desc")
        except NotFoundError:
            return None
        return [FilmShort(**hit)["_source"] for hit in doc["hits"]["hits"]]

    async def get_by_query(
            self, query: str, page_number: int, page_size: int
            ) -> Optional[FilmShort]:
        film = await self._get_qfilm_from_elastic(query, page_number, page_size)
        if not film:
            return None
        return film
    
    async def get_qfilm_from_elastic(
            self, film_name: str, page_number: int, page_size: int
            ) -> Optional[FilmShort]:
        try:
            query = {"match": {"title": film_name}}
            body = {
                    "from": page_number, "size": page_size, "query": query,
                    "_source": ["id", "imdb_rating", "title"]
                    }
            doc = await self.elastic.search(index="movies", body=body)
        except NotFoundError:
            return None
        return [FilmShort(**hit["fields"]) for hit in doc["hits"]["hits"]]
        


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
