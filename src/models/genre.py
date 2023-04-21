from models.mixins import JSONConfigMixin, UUIDMixin


class GenreShort(UUIDMixin, JSONConfigMixin):
    name: str


class Genre(GenreShort):
    popularity: float
    description: str
