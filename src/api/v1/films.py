from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from models.models import Film, FilmShort
from services.abc import FilmServiceABC
from services.film import get_film_service

router = APIRouter()


@router.get(
    "/{film_id}",
    response_model=Film,
    summary="Получить описание кинопроизведения",
    description="Подробное описание кинопроизведения",
    response_description="Идентификатор, наименование, рейтинг, описание, список жанров, краткое представления об участниках кинопроизведения",
    tags=['Детали'],
)
async def film_details(
    film_id: UUID, film_service: FilmServiceABC = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return Film(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


@router.get(
    "/",
    response_model=list[FilmShort],
    summary="Получить список фильмов",
    description="Список кинопроизведений с параметрами отбора, упорядочивания, пагинации",
    response_description="Список кратких представлений кинопроизведений",
    tags=['Списки'],
)
async def film_list(
    sort: str | None = None,
    genre_id: str | None = None,
    similar_to: str | None = None,
    page_size: Annotated[int, Query(gt=0)] = 50,
    page_number: Annotated[int, Query(gt=0)] = 1,
    film_service: FilmServiceABC = Depends(get_film_service),
) -> list[FilmShort]:
    films = await film_service.get_films(
        sort, page_size, page_number, genre_id, similar_to
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    films_to_return = [
        FilmShort(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
    return films_to_return


@router.get(
    "/search/",
    response_model=list[FilmShort],
    summary="Поиск по кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Идентификатор, название и рейтинг кинопроизведения",
    tags=['Полнотекстовый поиск'],
)
async def film_list_query(
    query: str = "",
    page_number: Annotated[int, Query(gt=0)] = 1,
    page_size: Annotated[int, Query(gt=0)] = 50,
    film_service: FilmServiceABC = Depends(get_film_service),
) -> list[FilmShort]:
    films = await film_service.get_by_query(query, page_number, page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    films_to_return = [
        FilmShort(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
    return films_to_return
