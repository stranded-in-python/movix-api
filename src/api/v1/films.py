from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()


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


@router.get(
    "/{film_id}",
    response_model=FilmDetailed,
    summary="Получить описание кинопроизведения",
    description="Подробное описание кинопроизведения",
    response_description="Идентификатор, наименование, рейтинг, описание, список жанров, краткое представления об участниках кинопроизведения",
    tags=['Детали'],
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> FilmDetailed:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return FilmDetailed(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


@router.get(
    "/",
    response_model=list[Film],
    summary="Получить список фильмов",
    description="Список кинопроизведений с параметрами отбора, упорядочивания, пагинации",
    response_description="Список кратких представлений кинопроизведений",
    tags=['Списки'],
)
async def film_list(
    sort: str | None = None,
    genre_id: str | None = None,
    similar_to: str | None = None,
    page_size: int = 50,
    page_number: int = 1,
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    films = await film_service.get_films(
        sort, page_size, page_number, genre_id, similar_to
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    films_to_return = [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
    return films_to_return


@router.get(
    "/search/",
    response_model=list[Film],
    summary="Поиск по кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Идентификатор, название и рейтинг кинопроизведения",
    tags=['Полнотекстовый поиск'],
)
async def film_list_query(
    query: str = "",
    page_number: int = 1,
    page_size: int = 50,
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    films = await film_service.get_by_query(query, page_number, page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    films_to_return = [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
    return films_to_return
