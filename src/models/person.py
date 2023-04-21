from models.film import FilmRoles
from models.mixins import JSONConfigMixin, UUIDMixin


class PersonShort(UUIDMixin, JSONConfigMixin):
    full_name: str


class Person(PersonShort):
    roles: list[str]
    films: list[FilmRoles]
