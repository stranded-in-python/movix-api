from functools import lru_cache
from uuid import UUID

from db.elastic import get_manager as get_elastic_manager
from models.models import Film, FilmRoles
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

    async def get_films(
        self, sort: str | None, pagination, genre_id: str | None, similar_to: str | None
    ) -> list[Film] | None:
        """Построить нужную query по фильмам в ElasticSearch
        в зависимости от наличия передаваемых в нее параметров"""
        filters = {}
        if genre_id:
            filters['genre_id'] = genre_id
        if similar_to:
            filters['similar_to'] = similar_to

        films = await self.storage.get_items(filters, sort, pagination)

        if not films:
            return None

        return [Film(**f.dict()) for f in films]

    async def get_by_query(self, query, pagination) -> list[Film] | None:
        films = await self.storage.get_by_query(query, None, pagination)

        if not films:
            return None

        return [Film(**f.dict()) for f in films]

    async def get_films_by_person(self, person_id: UUID, pagination) -> list[Film]:
        """Получить список фильмов в кратком представлении по персоне"""
        films = await self.storage.get_films_by_person(None, pagination, person_id)
        return [Film(**f.dict()) for f in films]

    async def get_films_with_roles_by_person(
        self, person_id: UUID, pagination
    ) -> list[FilmRoles]:
        """Получить фильмы персоны с его ролью"""
        return await self.storage.get_films_with_roles_by_person(
            None, pagination, person_id
        )


@lru_cache
def get_film_service() -> FilmService:
    return FilmService(storage=FilmElasticStorage(manager=get_elastic_manager))
