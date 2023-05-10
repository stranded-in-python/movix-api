import pytest

from tests.functional.conftest import client
from tests.functional.testdata.search_responses import *


class TestSearch:
    @pytest.mark.asyncio
    async def test_search_films_ok(self, client):
        response = await client.get(
            "/api/v1/films/search/?query=Star&page_number=1&page_size=2"
        )
        assert response.status_code == 200, response.text
        assert response.json() == SEARCH_FILMS_SUCCESS

    @pytest.mark.asyncio
    async def test_search_films_unprocessable(self, client):
        response = await client.get(
            "/api/v1/films/search/?query=Star&page_number=-1&page_size=2"
        )
        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_search_films_not_found(self, client):
        response = await client.get(
            "/api/v1/films/search/?query=jkngjrkt&page_number=1&page_size=2"
        )
        assert response.status_code == 404, response.text
        assert response.json() == SEARCH_FILMS_NOT_FOUND

    @pytest.mark.asyncio
    async def test_search_persons_ok(self, client):
        response = await client.get(
            "/api/v1/persons/search?query=Carrie&page_size=2&page_number=1"
        )
        assert response.status_code == 200, response.text
        assert response.json() == SEARCH_PERSONS_SUCCESS

    @pytest.mark.asyncio
    async def test_search_persons_unprocessable(self, client):
        response = await client.get(
            "/api/v1/persons/search?query=Carrie&page_size=-2&page_number=1"
        )
        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_search_persons_not_found(self, client):
        response = await client.get(
            "/api/v1/persons/search?query=ASJGNRIJGNRKJEG&page_size=2&page_number=1"
        )
        assert response.status_code == 404, response.text
        assert response.json() == SEARCH_PERSONS_NOT_FOUND
