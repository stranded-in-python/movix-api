from collections.abc import Callable
from functools import lru_cache
from uuid import UUID

from elasticsearch import NotFoundError

from db.abc import ElasticManagerABC
from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import Genre, GenreShort

from .abc import GenreServiceABC, GenreStorageABC
from .cache import cache_decorator


class GenreElasticStorage(GenreStorageABC):
    def __init__(self, manager: Callable[[], ElasticManagerABC]):
        self.manager = manager

    @cache_decorator(get_cache())
    async def get_item(self, item_id: UUID) -> GenreShort | None:
        try:
            doc = await self.manager().get(index='genres', id=item_id)

        except NotFoundError:
            return None

        return GenreShort(**doc.body['_source'])

    @cache_decorator(get_cache())
    async def get_genre_popularity(self, genre_id: UUID) -> float | None:
        query: dict = {
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
        }
        aggs: dict = {"avg_imdb_rating": {"avg": {"field": "imdb_rating"}}}

        try:
            results = await self.manager().search(
                index="movies", query=query, aggs=aggs
            )

        except NotFoundError:
            return None

        return results["aggregations"]["avg_imdb_rating"]["value"]

    @cache_decorator(get_cache())
    async def get_items(self) -> list[GenreShort | Genre] | None:
        query: dict = {"match_all": {}}
        source: list = ["id", "name"]

        try:
            doc = await self.manager().search(
                index="genres", query=query, source=source
            )

        except NotFoundError:
            return None

        return list(GenreShort(**hit["_source"]) for hit in doc.body['hits']['hits'])


class GenreService(GenreServiceABC):
    def __init__(self, storage: GenreStorageABC):
        self.storage = storage

    async def get_by_id(self, item_id: UUID) -> Genre | None:
        """Данные по конкретному жанру."""
        genre = await self.storage.get_item(item_id)

        if not genre:
            return None

        popularity = await self.storage.get_genre_popularity(item_id)

        return Genre(**dict(genre), popularity=popularity)

    async def get_genres(self) -> list[GenreShort] | None:
        """Получить список жанров"""
        return await self.storage.get_items()


@lru_cache
def get_genres_service() -> GenreService:
    return GenreService(storage=GenreElasticStorage(manager=get_elastic_manager))
