from http import HTTPStatus

import pytest

from tests.test_services.testdata import search_responses

pytestmark = pytest.mark.asyncio


class TestSearch:
    async def test_search_films_ok(self, client):
        response = await client.get(
            "/api/v1/films/search/?query=Star&page_number=1&page_size=2"
        )
        assert response.status_code == HTTPStatus.OK, response.text
        assert response.json() == search_responses.SEARCH_FILMS_SUCCESS

    async def test_search_films_unprocessable(self, client):
        response = await client.get(
            "/api/v1/films/search/?query=Star&page_number=-1&page_size=2"
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text

    async def test_search_films_not_found(self, client):
        response = await client.get(
            "/api/v1/films/search/?query=jkngjrkt&page_number=1&page_size=2"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, response.text
        assert response.json() == search_responses.SEARCH_FILMS_NOT_FOUND

    async def test_search_persons_ok(self, client):
        response = await client.get(
            "/api/v1/persons/search?query=Carrie&page_size=2&page_number=1"
        )
        assert response.status_code == HTTPStatus.OK, response.text
        assert response.json() == search_responses.SEARCH_PERSONS_SUCCESS

    async def test_search_persons_unprocessable(self, client):
        response = await client.get(
            "/api/v1/persons/search?query=Carrie&page_size=-2&page_number=1"
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text

    async def test_search_persons_not_found(self, client):
        response = await client.get(
            "/api/v1/persons/search?query=ASJGNRIJGNRKJEG&page_size=2&page_number=1"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, response.text
        assert response.json() == search_responses.SEARCH_PERSONS_NOT_FOUND
