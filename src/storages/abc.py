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
    async def get_item(self, item_id: UUID) -> BaseModel | None:
        ...

    @abstractmethod
    async def get_items(
        self,
        filters: dict[str, Any] | None = None,
        sort_order: str | None = None,
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
        filters: dict[str, Any] | None = None,
        sort_order: str | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[models.FilmShort] | None:
        ...

    @abstractmethod
    async def get_films_by_genre(
        self,
        sort_order: str | None,
        pagination: PaginateQueryParams | None,
        genre_id: UUID,
    ) -> list[models.FilmShort]:
        ...

    @abstractmethod
    async def get_similar_films(
        self,
        sort_order: str | None,
        pagination: PaginateQueryParams | None,
        film_id: UUID,
    ) -> list[models.FilmShort]:
        ...

    @abstractmethod
    async def get_by_query(
        self, query: str, sort_order: str | None, pagination: PaginateQueryParams | None
    ) -> list[models.FilmShort]:
        ...

    @abstractmethod
    async def get_films_by_person(
        self,
        sort_order: str | None,
        pagination: PaginateQueryParams | None,
        person_id: UUID,
    ) -> list[models.FilmShort]:
        ...

    @abstractmethod
    async def get_films_with_roles_by_person(
        self,
        sort_order: str | None,
        pagination: PaginateQueryParams | None,
        person_id: UUID,
    ) -> list[models.FilmRoles]:
        ...


class GenreStorageABC(StorageABC):
    @abstractmethod
    async def get_item(self, item_id: UUID) -> models.GenreShort | None:
        ...

    @abstractmethod
    async def get_genre_popularity(self, genre_id: UUID) -> float | None:
        ...

    @abstractmethod
    async def get_items(
        self,
        filters: dict[str, Any] | None = None,
        sort_order: str | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[models.GenreShort | models.Genre] | None:
        ...


class PersonStorageABC(StorageABC):
    @abstractmethod
    async def get_item(self, item_id: UUID) -> models.PersonShort | None:
        ...

    @abstractmethod
    async def get_items(
        self,
        filters: dict[str, Any] | None = None,
        sort_order: str | None = None,
        pagination: PaginateQueryParams | None = None,
    ) -> list[models.PersonShort] | None:
        ...
