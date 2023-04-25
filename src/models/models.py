from datetime import datetime

from models.mixins import JSONConfigMixin, UUIDMixin


class GenreShort(UUIDMixin, JSONConfigMixin):
    name: str


class FilmShort(UUIDMixin, JSONConfigMixin):
    title: str
    imdb_rating: float


class PersonShort(UUIDMixin, JSONConfigMixin):
    full_name: str


class Genre(GenreShort):
    popularity: float
    description: str


class Film(FilmShort):
    description: str
    creation_date: datetime
    genre: list[GenreShort]
    actors: list[PersonShort]
    writers: list[PersonShort]
    directors: list[PersonShort]


class FilmRoles(UUIDMixin, JSONConfigMixin):
    roles: list[str]


class Person(PersonShort):
    roles: list[str]
    films: list[FilmRoles]
