from functools import lru_cache
from typing import Optional

from elasticsearch import NotFoundError

from db.elastic import ElasticManager
from db.elastic import get_manager as get_elastic_manager
from db.redis import get_cache
from models.models import Film

from .cache import cache_decorator


class FilmService:
    def __init__(self, elastic: ElasticManager):
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._get_film_from_elastic(film_id)
        return film

    @cache_decorator(get_cache())
    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        elastic = self.elastic.get_client()
        try:
            doc = await elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])


@lru_cache
async def get_film_service() -> FilmService:
    return FilmService(get_elastic_manager())
