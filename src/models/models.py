from datetime import datetime

from models.mixins import UUIDMixin


class GenreShort(UUIDMixin):
    name: str


class FilmShort(UUIDMixin):
    title: str
    imdb_rating: float | None = None


class PersonShort(UUIDMixin):
    full_name: str


class Genre(GenreShort):
    popularity: float | None = None
    description: str | None = None


class Film(FilmShort):
    description: str | None = None
    genres: list[GenreShort]
    actors: list[PersonShort]
    writers: list[PersonShort]
    directors: list[PersonShort]
    creation_date: datetime | None = None


class FilmRoles(FilmShort):
    roles: list[str]


class Person(PersonShort):
    films: list[FilmRoles]
