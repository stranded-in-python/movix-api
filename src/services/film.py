from functools import lru_cache
from typing import Optional
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
        film = await self._get_film_from_elastic(film_id)
        return film

    @cache_decorator(get_cache())
    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await get_elastic_manager().get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    # Serge пока(?) без редис
    async def get_films(
        self,
        sort: str,
        page_size: int,
        page_number: int,
        genre_name: str,
        similar_to: str,
    ) -> Optional[FilmShort]:
        if genre_name and not similar_to:
            films = await self.get_films_by_genre(
                sort, page_size, page_number, genre_name
            )
        elif similar_to:
            films = await self.get_similar_films(
                sort, page_size, page_number, similar_to
            )
        films = await self._get_films_from_elastic(
            sort, page_size, page_number, genre_name, similar_to
        )
        if not films:
            return None
        return films

    async def get_films_by_genre(
        self, sort: str, page_size: int, page_number: int, genre_name: str
    ) -> Optional[FilmShort]:
        query = {
            "bool": {
                "filter": [{"terms": {"genre": [genre_name]}}]
            }  # ! пока что genre_name. Должен быть id
        }
        body = {
            "from": page_number,
            "size": page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await get_elastic_manager().search(
                index="movies", body=body, sort=f"{sort}:desc"
            )
        except NotFoundError:
            return None
        return [FilmShort(**hit)["_source"] for hit in doc["hits"]["hits"]]

    async def get_similar_films(
        self, sort: str, page_size: int, page_number: int, film_id: str
    ) -> Optional[FilmShort]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        genres_to_search = Film(**doc['_source']).genre
        query = {
            "bool": {
                "filter": [{"terms": {"genre": genres_to_search}}]
            }  # ! пока что genre_name. Должен быть id
        }
        body = {
            "from": page_number,
            "size": page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await get_elastic_manager().search(
                index="movies", body=body, sort=f"{sort}:desc"
            )
        except NotFoundError:
            return None

    async def _get_films_from_elastic(
        self, sort: str, page_number: int, page_size: int, genre_name, similar_to
    ) -> Optional[FilmShort]:
        query = {"match_all": {}}
        body = {
            "from": page_number,
            "size": page_size,
            "query": query,
            "_source": ["id", "imdb_rating", "title"],
        }
        try:
            doc = await get_elastic_manager().search(
                index="movies", body=body, sort=f"{sort}:desc"
            )
        except NotFoundError:
            return None
        return [FilmShort(**hit)["_source"] for hit in doc["hits"]["hits"]]

    async def get_by_query(
        self, query: str, page_number: int, page_size: int
    ) -> Optional[FilmShort]:
        film = await self._get_film_from_elastic(query, page_number, page_size)
        if not film:
            return None
        return film

    async def get_qfilm_from_elastic(
        self, film_name: str, page_number: int, page_size: int
    ) -> Optional[FilmShort]:
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
            return None
        return [FilmShort(**hit["fields"]) for hit in doc["hits"]["hits"]]

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
            return None

        return list(FilmShort(**hit["_source"]) for hit in doc["hits"]["hits"])


@lru_cache
def get_film_service() -> FilmService:
    return FilmService()
