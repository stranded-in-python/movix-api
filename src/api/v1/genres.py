from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.models import Genre, GenreShort
from services.genres import GenreService, get_genres_service

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genres_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return genre


@router.get("", response_model=list[GenreShort])
async def genre_list(
    genre_service: GenreService = Depends(get_genres_service),
) -> list[GenreShort]:
    genres = await genre_service.get_genres()

    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

    return genres
