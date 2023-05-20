from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.pagination import PaginateQueryParams
from models.models import Film, FilmShort
from services.abc import FilmServiceABC
from services.films import get_film_service

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
    pagination: PaginateQueryParams = Depends(PaginateQueryParams),
    film_service: FilmServiceABC = Depends(get_film_service),
) -> list[Film]:
    films = await film_service.get_films(sort, pagination, genre_id, similar_to)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return films


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
    pagination: PaginateQueryParams = Depends(PaginateQueryParams),
    film_service: FilmServiceABC = Depends(get_film_service),
) -> list[Film]:
    films = await film_service.get_by_query(query, pagination)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return films
