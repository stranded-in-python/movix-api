import logging
from functools import lru_cache
from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch, BadRequestError, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import Film, FilmShort

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

    async def get_films(
        self,
        sort: str,
        page_size: int,
        page_number: int,
        genre_id: str | None,
        similar_to: str | None,
    ) -> Optional[FilmShort]:
        """Построить нужную query по фильмам в ElasticSearch
        в зависимости от наличия передаваемых в нее параметров"""
        if sort[0] == "-":
            order = "desc"
        elif sort[0] == '+':
            order = "asc"
        else:
            return None
        sort = sort[1:]
        if genre_id and not similar_to:
            films = await self.get_films_by_genre(
                order, sort, page_size, page_number, genre_id
            )
        elif similar_to:
            films = await self.get_similar_films(
                order, sort, page_size, page_number, similar_to
            )
        else:
            films = await self._get_films_from_elastic(
                order, sort, page_number, page_size
            )
        if not films:
            return None
        return films

    @cache_decorator(get_cache())
    async def get_films_by_genre(
        self, order: str, sort: str, page_size: int, page_number: int, genre_id: str
    ) -> Optional[FilmShort]:
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
                index="movies", body=body, sort=f"{sort}:{order}"
            )
        except NotFoundError:
            return None
        films_raw = [hit["_source"] for hit in doc["hits"]["hits"]]
        to_return = [FilmShort(**elem) for elem in films_raw]
        return to_return

    @cache_decorator(get_cache())
    async def get_similar_films(
        self, order: str, sort: str, page_size: int, page_number: int, film_id: str
    ) -> Optional[FilmShort]:
        """Получить похожие фильмы. Похожими фильмами являются фильмы в одном жанре"""
        try:
            doc = await get_elastic_manager().get(index='movies', id=film_id)
        except NotFoundError:
            return None
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
                index="movies", body=body, sort=f"{sort}:{order}"
            )
        except NotFoundError:
            return None
        films_raw = [hit["_source"] for hit in doc["hits"]["hits"]]
        to_return = [FilmShort(**elem) for elem in films_raw]
        return to_return

    @cache_decorator(get_cache())
    async def _get_films_from_elastic(
        self, order: str, sort: str, page_number: int, page_size: int
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
                index="movies", body=body, sort=f"{sort}:{order}"
            )
        except NotFoundError:
            return None
        films_raw = [hit["_source"] for hit in doc["hits"]["hits"]]
        to_return = [FilmShort(**elem) for elem in films_raw]
        return to_return

    async def get_by_query(
        self, query: str, page_number: int, page_size: int
    ) -> Optional[FilmShort]:
        film = await self._get_qfilm_from_elastic(query, page_number, page_size)
        if not film:
            return None
        return film

    @cache_decorator(get_cache())
    async def _get_qfilm_from_elastic(
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
        films_raw = [hit["_source"] for hit in doc["hits"]["hits"]]
        to_return = [FilmShort(**elem) for elem in films_raw]
        return to_return


@lru_cache
def get_film_service() -> FilmService:
    return FilmService()
