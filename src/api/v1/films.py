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
# Проблемы
# 1.Запиливал, исходя из схемы предыдущего спринта. У жанров нет айдишников, поэтому сделал пока
# пока genre_name
# 2. Не использовал redis. Несколько объектов можно из него вытягивать так
# https://redis.io/commands/json.mget/
@router.get("/films", response_model=list[Film])
async def film_list(
    sort: str,
    page_size: int,
    page_number: int,
    genre_name=None,  # должен быть id
    similar_to=None,
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    films = await film_service.get_films(
        sort, page_size, page_number, genre_name, similar_to
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")
    return films


@router.get("/search", response_model=list[Film])
async def film_list(
    query: str,
    page_number: int,
    page_size: int,
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    film = await film_service.get_by_query(query, page_number, page_size)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return film
