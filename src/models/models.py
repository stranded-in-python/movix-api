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
    genres: list[GenreShort] | None = None
    actors: list[PersonShort] | None = None
    writers: list[PersonShort] | None = None
    directors: list[PersonShort] | None = None


class FilmRoles(FilmShort):
    roles: list[str]


class Person(PersonShort):
    films: list[FilmRoles]


class User(UUIDMixin):
    access_rights: list[str] | None = None
    auth_timeout: bool = False
