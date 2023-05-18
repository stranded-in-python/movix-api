from functools import lru_cache
from uuid import UUID





from db.elastic import get_manager as get_elastic_manager
from models.models import Film, FilmShort
from storages.abc import FilmStorageABC
from storages.storages import FilmElasticStorage

from .abc import FilmServiceABC


class FilmService(FilmServiceABC):
    def __init__(self, storage: FilmStorageABC):
        self.storage = storage

    async def get_by_id(self, item_id: UUID) -> Film | None:
        """Данные по конкретному жанру."""
        film = await self.storage.get_item(item_id)

        if not film:
            return None
        return Film(**dict(film))

    async def get_films(self,
        sort: str | None,
        pagination_params,
        genre_id: str | None,
        similar_to: str | None) -> list[FilmShort] | None:
        
        films = await self.storage.get_items(sort, pagination_params, genre_id, similar_to)

        if not films:
            return None
    
        return films

    async def get_by_query(self, query, pagination_params) -> list[FilmShort] | None:
        
        films = await self.storage.get_by_query(query, pagination_params)

        if not films:
            return None
        
        return films


@lru_cache
def get_film_service() -> FilmService:
    return FilmService(storage=FilmElasticStorage(manager=get_elastic_manager))
