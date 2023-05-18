from functools import lru_cache
from uuid import UUID

from db.elastic import get_manager as get_elastic_manager
from models.models import Genre, GenreShort
from storages.abc import GenreStorageABC
from storages.storages import GenreElasticStorage

from .abc import GenreServiceABC


class GenreService(GenreServiceABC):
    def __init__(self, storage: GenreStorageABC):
        self.storage = storage

    async def get_by_id(self, item_id: UUID) -> Genre | None:
        """Данные по конкретному жанру."""
        genre = await self.storage.get_item(item_id)

        if not genre:
            return None

        popularity = await self.storage.get_genre_popularity(item_id)

        return Genre(**dict(genre), popularity=popularity)

    async def get_genres(self) -> list[GenreShort] | None:
        """Получить список жанров"""
        return await self.storage.get_items()


@lru_cache
def get_genres_service() -> GenreService:
    return GenreService(storage=GenreElasticStorage(manager=get_elastic_manager))
