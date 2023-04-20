from src.models.film import FilmRoles
from src.models.mixins import UUIDMixin, JSONConfigMixin


class PersonShort(UUIDMixin, JSONConfigMixin):
    full_name: str


class Person(PersonShort):
    roles: list[str]
    films: list[FilmRoles]
