from abc import ABC, abstractmethod
from uuid import UUID

from models.models import Film, FilmRoles, FilmShort, Genre, GenreShort, PersonShort


class FilmServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, film_id: UUID) -> Film | None:
        ...

    @abstractmethod
    async def get_films(
        self,
        sort: str | None,
        page_size: int,
        page_number: int,
        genre_id: str | None,
        similar_to: str | None,
    ) -> list[FilmShort]:
        ...

    @abstractmethod
    async def get_similar_films(
        self, sort: str | None, page_size: int, page_number: int, film_id: str
    ) -> list[FilmShort]:
        ...

    @abstractmethod
    async def get_by_query(
        self, query: str, page_number: int, page_size: int
    ) -> list[FilmShort]:
        ...

    @abstractmethod
    async def get_films_by_genre(
        self, sort: str | None, page_size: int, page_number: int, genre_id: str
    ) -> list[FilmShort]:
        ...

    @abstractmethod
    async def get_films_with_roles_by_person(
        self,
        person_id: UUID,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> list[FilmRoles]:
        ...

    @abstractmethod
    async def get_films_by_person(
        self,
        person_id: UUID,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> list[FilmShort]:
        ...


class GenreServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        ...

    @abstractmethod
    async def get_genres(self) -> list[GenreShort] | None:
        ...


class PersonServiceABC(ABC):
    @abstractmethod
    async def get_by_id(self, person_id: UUID) -> PersonShort | None:
        ...

    @abstractmethod
    async def get_by_query(
        self, name: str, page_size: int | None = None, page_number: int | None = None
    ) -> list[PersonShort]:
        ...
