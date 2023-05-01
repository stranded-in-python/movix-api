from functools import lru_cache
from typing import Any, Optional
from uuid import UUID

from elasticsearch import NotFoundError

from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import Film, FilmRoles, FilmShort

from .cache import cache_decorator


class FilmService:
    def __init__(self):
        self._person_roles = {
            "actors_inner_hits": "actor",
            "directors_inner_hits": "director",
            "writers_inner_hits": "writer",
        }

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Получить фильм по ID"""
        film = await self._get_film_from_elastic(film_id)
        return film

    @cache_decorator(get_cache())
    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await get_elastic_manager().get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

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
        page_size: int,
        page_number: int,
        genre_id: str | None,
        similar_to: str | None,
    ) -> list[FilmShort]:
        """Построить нужную query по фильмам в ElasticSearch
        в зависимости от наличия передаваемых в нее параметров"""
        if genre_id and not similar_to:
            return await self.get_films_by_genre(sort, page_size, page_number, genre_id)
        if similar_to:
            return await self.get_similar_films(
                sort, page_size, page_number, similar_to
            )

        return await self._get_films_from_elastic(sort, page_number, page_size)

    @cache_decorator(get_cache())
    async def get_films_by_genre(
        self, sort: str | None, page_size: int, page_number: int, genre_id: str
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
            "from": page_number,
            "size": page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await get_elastic_manager().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator(get_cache())
    async def get_similar_films(
        self, sort: str | None, page_size: int, page_number: int, film_id: str
    ) -> list[FilmShort]:
        """Получить похожие фильмы. Похожими фильмами являются фильмы в одном жанре"""
        try:
            doc = await get_elastic_manager().get(index='movies', id=film_id)
        except NotFoundError:
            return []
        genres_to_search = [elem['name'] for elem in doc['_source']['genres']]
        query = {"bool": {"filter": [{"terms": {"genre": genres_to_search}}]}}
        body = {
            "from": page_number,
            "size": page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await get_elastic_manager().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    @cache_decorator(get_cache())
    async def _get_films_from_elastic(
        self, sort: str | None, page_number: int, page_size: int
    ) -> list[FilmShort]:
        query = {"match_all": {}}
        body = {
            "from": page_number,
            "size": page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await get_elastic_manager().search(
                index="movies", body=body, **self._sort_2_order(sort)
            )
        except NotFoundError:
            return []
        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    async def get_by_query(
        self, query: str, page_number: int, page_size: int
    ) -> list[FilmShort]:
        return await self._get_qfilm_from_elastic(query, page_number, page_size)

    @cache_decorator(get_cache())
    async def _get_qfilm_from_elastic(
        self, film_name: str, page_number: int, page_size: int
    ) -> list[FilmShort]:
        try:
            query = {"match": {"title": film_name}}
            body = {
                "from": page_number,
                "size": page_size,
                "query": query,
                "_source": ["id", "imdb_rating", "title"],
            }
            doc = await get_elastic_manager().search(index="movies", body=body)
        except NotFoundError:
            return []
        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]

    async def get_films_with_roles_by_person(
        self,
        person_id: UUID,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> list[FilmRoles]:
        """Получить фильмы персоны с его ролью"""

        return await self._get_films_with_roles_by_person_from_elastic(
            person_id, page_size, page_number
        )

    @cache_decorator(get_cache())
    async def _get_films_with_roles_by_person_from_elastic(
        self,
        person_id: UUID,
        page_size: int | None = None,
        page_number: int | None = None,
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

            docs = await get_elastic_manager().search(
                index="movies",
                query=query,
                source=source,
                size=page_size,
                from_=page_number,
            )

        except NotFoundError:
            return []

        return list(
            FilmRoles(**hit["_source"], roles=parse_roles(hit["inner_hits"]))
            for hit in docs["hits"]["hits"]
        )

    async def get_films_by_person(
        self,
        person_id: UUID,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> list[FilmShort]:
        """Получить список фильмов в кратком представлении по персоне"""
        return await self._get_films_by_person_from_elastic(
            person_id, page_size, page_number
        )

    @cache_decorator(get_cache())
    async def _get_films_by_person_from_elastic(
        self,
        person_id: UUID,
        page_size: int | None = None,
        page_number: int | None = None,
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

            doc = await get_elastic_manager().search(
                index="movies",
                query=query,
                source=source,
                size=page_size,
                from_=page_number,
            )

        except NotFoundError:
            return []

        return [FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"]]


@lru_cache
def get_film_service() -> FilmService:
    return FilmService()
