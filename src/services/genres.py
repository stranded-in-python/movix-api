from functools import lru_cache
from uuid import UUID

from elasticsearch import NotFoundError

from db.elastic import ElasticManager
from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import Genre, GenreShort

from .cache import cache_decorator

GENRE_CACHE_EXPIRE_IN_SECONDS = 24 * 60 * 60  # 24 hours


class GenreService:
    def __init__(self, elastic: ElasticManager):
        self.elastic: ElasticManager = elastic

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """Данные по конкретному жанру."""
        genre = await self._get_genre_from_elastic(genre_id)

        if not genre:
            return None

        popularity = await self._get_popularity_from_elastic(genre_id)

        return Genre(**dict(genre), popularity=popularity)

    async def get_genres(self) -> list[Genre] | None:
        """Получить список жанров"""
        genres = await self._get_genres_from_elastic()

        if not genres:
            return None

        return genres

    @cache_decorator(get_cache())
    async def _get_genre_from_elastic(self, genre_id: UUID) -> GenreShort | None:
        try:
            doc = await self.elastic._client.get(index='genres', id=genre_id)

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
            results = await self.elastic._client.search(
                index="movies", query=query, aggs=aggs
            )

        except NotFoundError:
            return None

        return results["aggregations"]["avg_imdb_rating"]["value"]

    @cache_decorator(get_cache())
    async def _get_genres_from_elastic(self) -> list[Genre] | None:
        query = {"match_all": {}}
        source = ["id", "name"]

        try:
            doc = await self.elastic._client.search(
                index="genres", query=query, source=source
            )

        except NotFoundError:
            return None

        return list(GenreShort(**hit["_source"]) for hit in doc.body['hits']['hits'])


@lru_cache
def get_genres_service() -> GenreService:
    return GenreService(get_elastic_manager())
