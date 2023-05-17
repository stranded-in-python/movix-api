from abc import abstractmethod
from collections.abc import Callable
from functools import lru_cache
from typing import Any, Optional
from uuid import UUID

from elasticsearch import NotFoundError

from db.abc import ElasticManagerABC
from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import Film, FilmRoles, FilmShort

from .abc import FilmServiceABC, StorageABC
from .cache import cache_decorator


class FilmStorageABC(StorageABC):
    @abstractmethod
    async def get_film(self, film_id: UUID) -> Optional[Film]:
        ...


class FilmElasticStorage(FilmStorageABC):
    def __init__(self, manager: Callable[[], ElasticManagerABC]):
        self.manager = manager

    @cache_decorator(get_cache())
    async def get_film(self, film_id: UUID) -> Optional[Film]:
        try:
            doc = await self.manager.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    def get_item(self, id: UUID):
        pass


class FilmService(FilmServiceABC):
    def __init__(self, storage: FilmStorageABC):
        self.storage = storage
        self._person_roles = {
            "actors_inner_hits": "actor",
            "directors_inner_hits": "director",
            "writers_inner_hits": "writer",
        }

    async def get_by_id(self, film_id: UUID) -> Optional[Film]:
        """Получить фильм по ID"""
        return await self.storage.get_film(film_id)

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

    async def get_films(
        self,
        sort: str | None,
        pagination_params,
        genre_id: str | None,
        similar_to: str | None,
    ) -> list[FilmShort]:
        """Построить нужную query по фильмам в ElasticSearch
        в зависимости от наличия передаваемых в нее параметров"""
        if genre_id and not similar_to:
            return await self.get_films_by_genre(sort, pagination_params, genre_id)
        if similar_to:
            return await self.get_similar_films(sort, pagination_params, similar_to)

        return await self._get_films_from_elastic(sort, pagination_params)

    @cache_decorator(get_cache())
    async def get_films_by_genre(
        self, sort: str | None, pagination_params, genre_id: str
    ) -> list[FilmShort]:
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
            doc = await self.storage().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator(get_cache())
    async def get_similar_films(
        self, sort: str | None, pagination_params, film_id: str
    ) -> list[FilmShort]:
        """Получить похожие фильмы. Похожими фильмами являются фильмы в одном жанре"""
        try:
            doc = await self.storage().get(index='movies', id=film_id)
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
            doc = await self.storage().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator(get_cache())
    async def _get_films_from_elastic(
        self, sort: str | None, pagination_params
    ) -> list[FilmShort]:
        query: dict = {"match_all": {}}
        body: dict = {
            "from": pagination_params.page_number,
            "size": pagination_params.page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await self.storage().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    async def get_by_query(self, query: str, pagination_params) -> list[FilmShort]:
        return await self._get_qfilm_from_elastic(query, pagination_params)

    @cache_decorator(get_cache())
    async def _get_qfilm_from_elastic(
        self, film_name: str, pagination_params
    ) -> list[FilmShort]:
        try:
            query = {"match": {"title": film_name}}
            body = {
                "from": pagination_params.page_number,
                "size": pagination_params.page_size,
                "query": query,
                "_source": ["id", "imdb_rating", "title"],
            }
            doc = await self.storage().search(index="movies", body=body)
        except NotFoundError:
            return []
        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    async def get_films_with_roles_by_person(
        self, person_id: UUID, pagination_params
    ) -> list[FilmRoles]:
        """Получить фильмы персоны с его ролью"""

        return await self._get_films_with_roles_by_person_from_elastic(
            person_id, pagination_params
        )

    @cache_decorator(get_cache())
    async def _get_films_with_roles_by_person_from_elastic(
        self, person_id: UUID, pagination_params
    ) -> list[FilmRoles]:
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

            docs = await self.storage().search(
                index="movies",
                query=query,
                source=source,
                size=pagination_params.page_size,
                from_=pagination_params.page_number,
            )

        except NotFoundError:
            return []

        return list(
            FilmRoles(**hit["_source"], roles=parse_roles(hit["inner_hits"]))
            for hit in docs["hits"]["hits"]
        )

    async def get_films_by_person(
        self, person_id: UUID, pagination_params
    ) -> list[FilmShort]:
        """Получить список фильмов в кратком представлении по персоне"""
        return await self._get_films_by_person_from_elastic(
            person_id, pagination_params
        )

    @cache_decorator(get_cache())
    async def _get_films_by_person_from_elastic(
        self, person_id: UUID, pagination_params
    ) -> list[FilmShort]:
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

            doc = await self.storage().search(
                index="movies",
                query=query,
                source=source,
                size=pagination_params.page_size,
                from_=pagination_params.page_number,
            )

        except NotFoundError:
            return []

        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]


@lru_cache
def get_film_service() -> FilmService:
    return FilmService(storage=get_elastic_manager)
