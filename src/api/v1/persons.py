from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.models import FilmShort, Person
from services.film import FilmService, get_film_service
from services.persons import PersonService, QueryParamPerson, get_persons_service

router = APIRouter()


@router.get("/{person_id}", response_model=Person)
async def person_details(
    person_id: str, persons_service: PersonService = Depends(get_persons_service)
) -> Person:
    """/api/v1/persons/<uuid:UUID>/"""
    person = await persons_service.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return person


@router.get("/search", response_model=list[Person])
async def person_list(
    search_params: QueryParamPerson,
    persons_service: PersonService = Depends(get_persons_service),
) -> list[Person]:
    """/api/v1/persons/search?query=captain&page_number=1&page_size=50"""

    return persons_service.get_by_query(search_params)


@router.get("/{person_id}/film", response_model=Person)
async def person_films(
    person_id: str,
    persons_service: PersonService = Depends(get_persons_service),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    """/api/v1/persons/<uuid:UUID>/film/"""
    person = await persons_service.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    films = await film_service.get_person_films(person_id)

    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return films
