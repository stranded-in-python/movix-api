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
        pagination_params: PaginateQueryParams,
        genre_id: str | None,
        similar_to: str | None,
    ) -> list[models.FilmShort]:
        ...

    @abstractmethod
    async def get_by_query(
        self, query: str, pagination_params: PaginateQueryParams
    ) -> list[models.FilmShort]:
        ...

    @abstractmethod
    async def get_films_with_roles_by_person(
        self, person_id: UUID, pagination_params: PaginateQueryParams
    ) -> list[models.FilmRoles]:
        ...

    @abstractmethod
    async def get_films_by_person(
        self, person_id: UUID, pagination_params: PaginateQueryParams
    ) -> list[models.FilmShort]:
        ...


class GenreServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, genre_id: UUID) -> models.Genre | None:
        ...

    @abstractmethod
    async def get_genres(self) -> list[models.GenreShort] | None:
        ...


class PersonServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, person_id: UUID) -> models.PersonShort | None:
        ...

    @abstractmethod
    async def get_by_query(
        self, name: str, page_size: int | None = None, page_number: int | None = None
    ) -> list[models.PersonShort]:
        ...
