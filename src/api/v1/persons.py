from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from api.v1.params import QueryParamPersonId, QueryParamPersonName
from models.models import FilmShort, Person
from services.film import FilmService, get_film_service
from services.persons import PersonService, get_persons_service

router = APIRouter()


@router.get("/{id}", response_model=Person)
async def person_details(
    params: QueryParamPersonId,
    persons_service: PersonService = Depends(get_persons_service),
    film_service: FilmService = Depends(get_film_service),
) -> Person:
    """/api/v1/persons/<uuid:UUID>/"""
    person = await persons_service.get_by_id(params.id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    films = await film_service.get_films_by_person(**params)

    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return Person(**person, films=films)


@router.get("/search", response_model=list[Person])
async def person_list(
    search_params: QueryParamPersonName,
    persons_service: PersonService = Depends(get_persons_service),
) -> list[Person]:
    """/api/v1/persons/search?query=captain&page_number=1&page_size=50"""

    return persons_service.get_by_query(**search_params)


@router.get("/{id}/film", response_model=Person)
async def person_films(
    params: QueryParamPersonId,
    persons_service: PersonService = Depends(get_persons_service),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    """/api/v1/persons/<uuid:UUID>/film/"""
    person = await persons_service.get_by_id(params.id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    films = await film_service.get_person_films(**params)

    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return films
