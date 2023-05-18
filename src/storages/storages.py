from typing import Callable
from uuid import UUID

from elasticsearch import NotFoundError

import models.models as models
from cache import cache_decorator
from db.abc import ElasticManagerABC

from .abc import GenreStorageABC, PersonStorageABC


class GenreElasticStorage(GenreStorageABC):
    def __init__(self, manager: Callable[[], ElasticManagerABC]):
        self.manager = manager

    @cache_decorator()
    async def get_item(self, item_id: UUID) -> models.GenreShort | None:
        try:
            doc = await self.manager().get(index='genres', id=item_id)

        except NotFoundError:
            return None

        return models.GenreShort(**doc.body['_source'])

    @cache_decorator()
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

    @cache_decorator()
    async def get_items(self) -> list[models.GenreShort | models.Genre] | None:
        query: dict = {"match_all": {}}
        source: list = ["id", "name"]

        try:
            doc = await self.manager().search(
                index="genres", query=query, source=source
            )

        except NotFoundError:
            return None

        return list(
            models.GenreShort(**hit["_source"]) for hit in doc.body['hits']['hits']
        )


class PersonElasticStorage(PersonStorageABC):
    def __init__(self, manager: Callable[[], ElasticManagerABC]):
        self.manager = manager

    @cache_decorator()
    async def get_item(self, person_id: UUID) -> models.PersonShort | None:
        try:
            doc = await self.manager().get(index='persons', id=person_id)

        except NotFoundError:
            return None

        return models.PersonShort(**doc.body['_source'])

    @cache_decorator()
    async def get_items(
        self, filters: str, pagination_params
    ) -> list[models.PersonShort]:
        query = {"match": {"full_name": filters}}
        source = ["id", "full_name"]

        try:
            doc = await self.manager().search(
                index="persons",
                query=query,
                source=source,
                from_=pagination_params.page_number,
                size=pagination_params.page_size,
            )

        except NotFoundError:
            return []

        return list(models.PersonShort(**hit["_source"]) for hit in doc["hits"]["hits"])
