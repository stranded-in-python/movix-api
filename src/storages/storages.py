from typing import Any, Callable, cast
from uuid import UUID

from elasticsearch import NotFoundError

import models.models as models
from cache import cache_decorator
from core.pagination import PaginateQueryParams
from db.abc import ElasticManagerABC

from .abc import FilmStorageABC, GenreStorageABC, PersonStorageABC


class ElasticUtilsMixin:
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

    def pagination_2_query_args(
        self, pagination: None | PaginateQueryParams
    ) -> dict[str, int]:
        if not pagination:
            return {}
        return {"from": pagination.page_number, "size": pagination.page_size}


class FilmElasticStorage(ElasticUtilsMixin, FilmStorageABC):
    def __init__(self, manager: Callable[[], ElasticManagerABC]):
        self.manager = manager
        self._person_roles = {
            "actors_inner_hits": "actor",
            "directors_inner_hits": "director",
            "writers_inner_hits": "writer",
        }

    @cache_decorator()
    async def _get_films_from_elastic(
        self, sort_order: str | None, pagination
    ) -> list[models.FilmShort] | None:
        query: dict = {"match_all": {}}
        body: dict = {
            **self.pagination_2_query_args(pagination),
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }

        try:
            doc = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort_order)
            )
        except NotFoundError:
            return None
        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator()
    async def get_item(self, item_id: UUID) -> models.FilmShort | None:
        try:
            doc = await self.manager().get(index='movies', id=item_id)

        except NotFoundError:
            return None

        return models.Film(**doc.body['_source'])

    async def get_items(
        self,
        filters: dict[str, Any] | None = None,
        sort_order: str | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[models.FilmShort] | None:
        if not filters:
            filters = {}

        if 'similar_to' in filters:
            return await self.get_similar_films(
                sort_order, pagination, cast(UUID, filters.get('similar_to'))
            )
        if 'genre_id' in filters:
            return await self.get_films_by_genre(
                sort_order, pagination, cast(UUID, filters.get('genre_id'))
            )

        return await self._get_films_from_elastic(sort_order, pagination)

    @cache_decorator()
    async def get_films_by_genre(
        self,
        sort_order: str | None,
        pagination: PaginateQueryParams | None,
        genre_id: UUID,
    ) -> list[models.FilmShort] | None:
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
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
            **self.pagination_2_query_args(pagination),
        }

        try:
            doc = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort_order)
            )
        except NotFoundError:
            return None
        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator()
    async def get_similar_films(
        self,
        sort_order: str | None,
        pagination: PaginateQueryParams | None,
        film_id: UUID,
    ) -> list[models.FilmShort] | None:
        """Получить похожие фильмы. Похожими фильмами являются фильмы в одном жанре"""
        try:
            doc = await self.manager().get(index='movies', id=film_id)
        except NotFoundError:
            return None
        genres_to_search = [elem['name'] for elem in doc['_source']['genres']]
        query = {"bool": {"filter": [{"terms": {"genre": genres_to_search}}]}}
        body = {
            **self.pagination_2_query_args(pagination),
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        if pagination:
            body["from"] = pagination.page_number
            body["size"] = pagination.page_size

        try:
            doc = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort_order)
            )
        except NotFoundError:
            return None
        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator()
    async def get_by_query(
        self, query: str, sort_order: str | None, pagination: PaginateQueryParams
    ) -> list[models.FilmShort] | None:
        try:
            elastic_query = {"match": {"title": query}}
            body = {
                **self.pagination_2_query_args(pagination),
                "query": elastic_query,
                "_source": ["id", "imdb_rating", "title"],
            }

            doc = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort_order)
            )
        except NotFoundError:
            return None
        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator()
    async def get_films_by_person(
        self,
        sort_order: str | None,
        pagination: PaginateQueryParams | None,
        person_id: UUID,
    ) -> list[models.FilmShort] | None:
        try:
            query = {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"match": {"actors.id": person_id}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"match": {"writers.id": person_id}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"match": {"directors.id": person_id}},
                            }
                        },
                    ]
                }
            }
            source = ["id", "imdb_rating", "title"]

            body = {
                **self.pagination_2_query_args(pagination),
                "query": query,
                "_source": source,
            }

            doc = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort_order)
            )

        except NotFoundError:
            return None

        return [models.FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator()
    async def get_films_with_roles_by_person(
        self,
        sort_order: str | None,
        pagination: PaginateQueryParams | None,
        person_id: UUID,
    ) -> list[models.FilmRoles] | None:
        def parse_roles(inner_hits: dict) -> list[str]:
            return list(
                self._person_roles[name]
                for name, hit in inner_hits.items()
                if bool(hit["hits"]["total"]["value"]) and name in self._person_roles
            )

        try:
            query = {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"match": {"actors.id": person_id}},
                                "inner_hits": {"name": "actors_inner_hits", "size": 0},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"match": {"writers.id": person_id}},
                                "inner_hits": {"name": "writers_inner_hits", "size": 0},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"match": {"directors.id": person_id}},
                                "inner_hits": {
                                    "name": "directors_inner_hits",
                                    "size": 0,
                                },
                            }
                        },
                    ]
                }
            }
            source = ["id", "imdb_rating", "title"]

            body = {
                **self.pagination_2_query_args(pagination),
                "query": query,
                "_source": source,
            }

            docs = await self.manager().search(
                index="movies", body=body, **self._sort_2_order(sort_order)
            )

        except NotFoundError:
            return None

        return list(
            models.FilmRoles(**hit["_source"], roles=parse_roles(hit["inner_hits"]))
            for hit in docs["hits"]["hits"]
        )


class GenreElasticStorage(ElasticUtilsMixin, GenreStorageABC):
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
    async def get_items(
        self,
        filters: dict[str, Any] | None = None,
        sort_order: str | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[models.GenreShort | models.Genre] | None:
        query: dict = {"match_all": {}}
        source: list = ["id", "name"]
        body = {
            **self.pagination_2_query_args(pagination),
            'query': query,
            '_source': source,
        }

        if not filters:
            pass

        try:
            doc = await self.manager().search(
                index="genres", body=body, **self._sort_2_order(sort_order)
            )

        except NotFoundError:
            return None

        return list(
            models.GenreShort(**hit["_source"]) for hit in doc.body['hits']['hits']
        )


class PersonElasticStorage(ElasticUtilsMixin, PersonStorageABC):
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
        self,
        filters: dict[str, Any] | None = None,
        sort_order: str | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[models.PersonShort] | None:
        if not filters:
            filters = {}

        query = {"match": {"full_name": filters.get('name')}}
        source = ["id", "full_name"]
        body = {
            **self.pagination_2_query_args(pagination),
            'query': query,
            '_source': source,
        }

        try:
            doc = await self.manager().search(
                index="persons", body=body, **self._sort_2_order(sort_order)
            )

        except NotFoundError:
            return None

        return list(models.PersonShort(**hit["_source"]) for hit in doc["hits"]["hits"])
