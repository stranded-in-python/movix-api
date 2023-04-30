from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.models import FilmShort, Person
from services.film import FilmService, get_film_service
from services.persons import PersonService, get_persons_service

router = APIRouter()


@router.get("/search", response_model=list[Person])
async def person_list(
    query: str,
    page_size: int | None = None,
    page_number: int | None = None,
    persons_service: PersonService = Depends(get_persons_service),
    film_service: FilmService = Depends(get_film_service),
) -> list[Person]:
    persons = await persons_service.get_by_query(query, page_size, page_number)

    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="persons not found"
        )

    return [
        Person(
            **dict(person),
            films=await film_service.get_films_with_roles_by_person(person.id),
        )
        for person in persons
    ]


@router.get("/{person_id}", response_model=Person)
async def person_details(
    person_id: UUID,
    page_size: int | None = None,
    page_number: int | None = None,
    persons_service: PersonService = Depends(get_persons_service),
    film_service: FilmService = Depends(get_film_service),
) -> Person:
    person = await persons_service.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    films = await film_service.get_films_with_roles_by_person(
        person_id, page_size, page_number
    )

    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return Person(**dict(person), films=films)


@router.get("/{person_id}/film", response_model=list[FilmShort])
async def person_films(
    person_id: UUID,
    page_size: int | None = None,
    page_number: int | None = None,
    persons_service: PersonService = Depends(get_persons_service),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    person = await persons_service.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    films = await film_service.get_films_by_person(person_id, page_size, page_number)

    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return films
