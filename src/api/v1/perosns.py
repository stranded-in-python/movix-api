from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from models.models import FilmShort, Person
from services.persons import PersonService, QueryPerson, get_persons_service

router = APIRouter()


@router.get("/{person_id}", response_model=Person)
async def person_details(
    person_id: str, persons_service: PersonService = Depends(get_persons_service)
) -> Person:
    """/api/v1/persons/<uuid:UUID>/"""
    person = persons_service.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person


@router.get("/search", response_model=list[Person])
async def person_list(
    persons_service: PersonService = Depends(get_persons_service), **kwargs
) -> list[Person]:
    """/api/v1/persons/search?query=captain&page_number=1&page_size=50"""
    try:
        query = QueryPerson(**kwargs)

    except ValidationError:
        # TODO Сформировать список невалидных параметров
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="bad list params"
        )

    return persons_service.get_by_query(query)


@router.get("/{person_id}/film", response_model=Person)
async def person_films(
    person_id: str, persons_service: PersonService = Depends(get_persons_service)
) -> list[FilmShort]:
    """/api/v1/persons/<uuid:UUID>/film/"""
    films = await persons_service.get_person_films(person_id)

    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return films
