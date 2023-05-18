from abc import ABC, abstractmethod
from uuid import UUID

import models.models as models


class FilmServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, film_id: UUID) -> models.Film | None:
        ...

    @abstractmethod
    async def get_films(
        self,
        sort: str | None,
        page_size: int,
        page_number: int,
        genre_id: str | None,
        similar_to: str | None,
    ) -> list[models.FilmShort]:
        ...

    @abstractmethod
    async def get_by_query(
        self, query: str, page_number: int, page_size: int
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
