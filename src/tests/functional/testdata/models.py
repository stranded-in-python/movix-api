# не уверен что они нужны

from uuid import UUID
from pydantic import BaseModel

class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class FilmDetailed(Film):
    description: str | None = None
    genre: list
    actors: list
    writers: list
    directors: list