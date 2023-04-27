from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Genre, GenreShort

GENRE_CACHE_EXPIRE_IN_SECONDS = 24 * 60 * 60  # 24 hours


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._get_genre_from_cache(genre_id)

        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)

            if not genre:
                return None

            await self._put_genre_to_cache(genre)

        return genre

    async def get_genres(self) -> Optional[list[Genre]]:
        genres = await self._get_genres_from_cache()

        if not genres:
            genres = await self._get_genres_from_elastic()

            if not genres:
                return None

            await self._put_genres_to_cache(genres)

        return genres

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[GenreShort]:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)

        except NotFoundError:
            return None

        try:
            popularity = self._get_popularity_from_elastic(genre_id)

        except NotFoundError:
            return None

        return Genre(**doc, popularity=popularity)

    async def _get_popularity_from_elastic(self, genre_id: str) -> float:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"exists": {"field": "imdb_rating"}},
                        {
                            "nested": {
                                "path": "genres",
                                "query": {"match": {"genres.id": genre_id}},
                            }
                        },
                    ]
                }
            },
            "aggs": {"avg_imdb_rating": {"avg": {"field": "imdb_rating"}}},
        }
        body = {"query": query, "size": 1}

        try:
            results = await self.elastic.search(index="genres", body=body)

        except NotFoundError:
            return None

        return results["aggregations"]["avg_imdb_rating"]["value"]

    async def _get_genres_from_elastic(self) -> Optional[list[Genre]]:
        query = {"match_all": {}}
        body = {"query": query, "_source": ["id", "name"]}

        try:
            doc = await self.elastic.search(index="genres", body=body)

        except NotFoundError:
            return None

        return [GenreShort(**hit)["_source"] for hit in doc["hits"]["hits"]]

    async def _get_genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        ...

    async def _get_genres_from_cache(self) -> Optional[list[Genre]]:
        ...

    async def _put_genre_to_cache(self, genre: Genre) -> None:
        ...

    async def _put_genres_to_cache(self, genres: list[GenreShort]) -> None:
        ...


@lru_cache
def get_genres_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
