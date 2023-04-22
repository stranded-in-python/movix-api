from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float

@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return Film(id=film.id, title=film.title, imdb_rating=film.imdb_rating)

# Serge
@router.get("/films", response_model=List[Film])
async def film_list(
        sort: str, page_size: int, page_number: int, 
        genre_name=None, # должен быть id
        film_service: FilmService = Depends(get_film_service)
) -> List[Film]:
    films = await film_service.get_films(sort, page_size, page_number, genre_name)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")
    return films