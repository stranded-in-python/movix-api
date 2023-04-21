from datetime import datetime

from models.genre import GenreShort
from models.mixins import JSONConfigMixin, UUIDMixin
from models.person import PersonShort


class FilmShort(UUIDMixin, JSONConfigMixin):
    title: str
    imdb_rating: float


class Film(FilmShort):
    description: str
    creation_date: datetime
    genre: list[GenreShort]
    actors: list[PersonShort]
    writers: list[PersonShort]
    directors: list[PersonShort]


class FilmRoles(UUIDMixin, JSONConfigMixin):
    roles: list[str]
