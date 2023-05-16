from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.models import Genre, GenreShort
from services.abc import GenreServiceABC
from services.genres import get_genres_service

router = APIRouter()


@router.get(
    "/{genre_id}",
    response_model=Genre,
    summary="Получить описание жанра",
    description="Подробное описание жанра кинопроизведений",
    response_description="Идентификатор, наименование, описание, популярность жанра",
    tags=['Детали'],
)
async def genre_details(
    genre_id: UUID, genre_service: GenreServiceABC = Depends(get_genres_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return genre


@router.get(
    "",
    response_model=list[GenreShort],
    summary="Получить список жанров",
    description="Список жанров кинопроизведений",
    response_description="Список кратких представлений жанра",
    tags=['Списки'],
)
async def genre_list(
    genre_service: GenreServiceABC = Depends(get_genres_service),
) -> list[GenreShort]:
    genres = await genre_service.get_genres()

    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

    return genres
