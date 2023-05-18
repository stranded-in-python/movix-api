from typing import Callable, Any
from uuid import UUID

from elasticsearch import NotFoundError

import models.models as models
from cache import cache_decorator
from db.abc import ElasticManagerABC

from .abc import FilmStorageABC, GenreStorageABC, PersonStorageABC


class FilmElasticStorage(FilmStorageABC):
    def __init__(self, manager: Callable[[], ElasticManagerABC]):
        self.manager = manager

    @cache_decorator()
    async def get_item(self, item_id: UUID) -> models.FilmShort | None:
        try:
            doc = await self.manager().get(index='movies', id=item_id)

        except NotFoundError:
            return None

        return models.Film(**doc.body['_source'])

    def _sort_2_order(self, sort: str | None) -> dict[str, Any]:
        if not sort:
            return {"sort": "id:asc"}

        match sort[0]:
            case "+":
                return {"sort": f"{sort[1:]}:asc"}
            case "-":
                return {"sort": f"{sort[1:]}:desc"}
            case _:
                return {"sort": "id:asc"}

    async def get_items(
        self,
        sort: str | None,
        pagination_params,
        genre_id: str | None,
        similar_to: str | None,
    ) -> list[models.FilmShort] | None:
        

        if genre_id and not similar_to:
            return await self.get_films_by_genre(sort, pagination_params, genre_id)
        if similar_to:
            return await self.get_similar_films(sort, pagination_params, similar_to)

        return await self._get_films_from_elastic(sort, pagination_params)
        
    @cache_decorator()
    async def get_films_by_genre(self, sort, pagination_params, genre_id):
        query = {
            "bool": {
                "must": [
                    {
                        "nested": {
                            "path": "genres",
                            "query": {
                                "bool": {"must": [{"match": {"genres.id": genre_id}}]}
                            },
                        }
                    }
                ]
            }
        }
        body = {
            "from": pagination_params.page_number,
            "size": pagination_params.page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]


    @cache_decorator()
    async def get_similar_films(
        self, sort: str | None, pagination_params, film_id: str
    ) -> list[models.FilmShort]:
        """Получить похожие фильмы. Похожими фильмами являются фильмы в одном жанре"""
        try:
            doc = await self.manager().get(index='movies', id=film_id)
        except NotFoundError:
            return []
        genres_to_search = [elem['name'] for elem in doc['_source']['genres']]
        query = {"bool": {"filter": [{"terms": {"genre": genres_to_search}}]}}
        body = {
            "from": pagination_params.page_number,
            "size": pagination_params.page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]
    
    @cache_decorator()
    async def _get_films_from_elastic(
        self, sort: str | None, pagination_params
    ) -> list[models.FilmShort]:
        query: dict = {"match_all": {}}
        body: dict = {
            "from": pagination_params.page_number,
            "size": pagination_params.page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator()
    async def get_by_query(self, query: str, pagination_params) -> list[models.FilmShort]:
        try:
            elastic_query = {"match": {"title": query}}
            body = {
                "from": pagination_params.page_number,
                "size": pagination_params.page_size,
                "query": elastic_query,
                "_source": ["id", "imdb_rating", "title"],
            }
            doc = await self.manager().search(index="movies", body=body)
        except NotFoundError:
            return []
        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]


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
