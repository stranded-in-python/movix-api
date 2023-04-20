from src.models.mixins import UUIDMixin, JSONConfigMixin


class GenreShort(UUIDMixin, JSONConfigMixin):
    name: str


class Genre(GenreShort):
    popularity: float
    description: str
