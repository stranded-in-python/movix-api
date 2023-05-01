from functools import lru_cache
from uuid import UUID

from elasticsearch import NotFoundError

from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import Genre, GenreShort

from .cache import cache_decorator


class GenreService:
    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """Данные по конкретному жанру."""
        genre = await self._get_genre_from_elastic(genre_id)

        if not genre:
            return None

        popularity = await self._get_popularity_from_elastic(genre_id)

        return Genre(**dict(genre), popularity=popularity)

    async def get_genres(self) -> list[GenreShort] | None:
        """Получить список жанров"""
        return await self._get_genres_from_elastic()

    @cache_decorator(get_cache())
    async def _get_genre_from_elastic(self, genre_id: UUID) -> GenreShort | None:
        try:
            doc = await get_elastic_manager().get(index='genres', id=genre_id)

        except NotFoundError:
            return None

        return GenreShort(**doc.body['_source'])

    @cache_decorator(get_cache())
    async def _get_popularity_from_elastic(self, genre_id: UUID) -> float | None:
        query = {
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
        aggs = {"avg_imdb_rating": {"avg": {"field": "imdb_rating"}}}

        try:
            results = await get_elastic_manager().search(
                index="movies", query=query, aggs=aggs
            )

        except NotFoundError:
            return None

        return results["aggregations"]["avg_imdb_rating"]["value"]

    @cache_decorator(get_cache())
    async def _get_genres_from_elastic(self) -> list[GenreShort | Genre] | None:
        query = {"match_all": {}}
        source = ["id", "name"]

        try:
            doc = await get_elastic_manager().search(
                index="genres", query=query, source=source
            )

        except NotFoundError:
            return None

        return list(GenreShort(**hit["_source"]) for hit in doc.body['hits']['hits'])


@lru_cache
def get_genres_service() -> GenreService:
    return GenreService()
