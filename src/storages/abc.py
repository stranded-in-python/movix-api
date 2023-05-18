from abc import ABC, abstractmethod
from typing import Any, Callable
from uuid import UUID

from pydantic import BaseModel

import models.models as models
from core.pagination import PaginateQueryParams
from db.abc import DBManager


class StorageABC(ABC):
    @abstractmethod
    def __init__(self, manager: Callable[[], DBManager]):
        self.manager = manager

    @abstractmethod
    def get_item(self, item_id: str) -> BaseModel | None:
        ...

    @abstractmethod
    def get_items(
        self,
        filters: str | None = None,
        sort_order: dict[str, Any] | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[BaseModel]:
        ...


class FilmStorageABC(StorageABC):
    @abstractmethod
    async def get_item(self, item_id: UUID) -> models.Film | None:
        ...    

    @abstractmethod
    async def get_items(
        self,
        filters: str | None = None,
        sort_order: dict[str, Any] | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[models.FilmShort] | None:
        ...


class GenreStorageABC(StorageABC):
    @abstractmethod
    async def get_item(self, item_id: UUID) -> models.GenreShort | None:
        ...

    @abstractmethod
    async def get_genre_popularity(self, genre_id: UUID) -> float | None:
        ...

    @abstractmethod
    async def get_items(self) -> list[models.GenreShort | models.Genre] | None:
        ...


class PersonStorageABC(StorageABC):
    @abstractmethod
    async def get_item(self, item_id: UUID) -> models.PersonShort | None:
        ...

    @abstractmethod
    async def get_items(
        self,
        filters: str | None = None,
        sort_order: dict[str, Any] | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[models.PersonShort] | None:
        ...
