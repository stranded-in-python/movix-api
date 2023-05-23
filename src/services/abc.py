from abc import ABC, abstractmethod
from uuid import UUID

import models.models as models
from core.pagination import PaginateQueryParams


class FilmServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, film_id: UUID) -> models.Film | None:
        ...

    @abstractmethod
    async def get_films(
        self,
        sort: str | None,
        pagination: PaginateQueryParams | None,
        genre_id: str | None,
        similar_to: str | None,
    ) -> list[models.Film]:
        ...

    @abstractmethod
    async def get_by_query(
        self, query: str, pagination: PaginateQueryParams | None
    ) -> list[models.Film]:
        ...

    @abstractmethod
    async def get_films_with_roles_by_person(
        self, person_id: UUID, pagination: PaginateQueryParams | None
    ) -> list[models.FilmRoles]:
        ...

    @abstractmethod
    async def get_films_by_person(
        self, person_id: UUID, pagination: PaginateQueryParams | None
    ) -> list[models.Film]:
        ...


class GenreServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, genre_id: UUID) -> models.Genre | None:
        ...

    @abstractmethod
    async def get_genres(self) -> list[models.Genre] | None:
        ...


class PersonServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, person_id: UUID) -> models.Person | None:
        ...

    @abstractmethod
    async def get_by_query(
        self, name: str, pagination: PaginateQueryParams | None
    ) -> list[models.Person]:
        ...
