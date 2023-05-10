import pytest

from tests.functional.conftest import client
from tests.functional.testdata.films_responses import (
    FILM_DETAILED_SUCCESS,
    FILM_DETAILED_UNPROCESSABLE,
)


class TestFilm:
    @pytest.mark.asyncio
    async def test_get_by_id_ok(self, client):
        response = await client.get(
            "/api/v1/films/0312ed51-8833-413f-bff5-0e139c11264a"
        )
        assert response.status_code == 200, response.text
        assert response.json() == FILM_DETAILED_SUCCESS

    @pytest.mark.asyncio
    async def test_get_by_id_notfound(self, client):
        response = await client.get(
            "/api/v1/films/0311ed51-8833-413f-bff5-0e139c11264a"
        )
        assert response.status_code == 404, response.text

    @pytest.mark.asyncio
    async def test_get_by_id_unprocessable(self, client):
        response = await client.get("/api/v1/films/-1")
        assert response.status_code == 422, response.text
        assert response.json() == FILM_DETAILED_UNPROCESSABLE

    @pytest.mark.asyncio
    async def test_get_film_list(self, client):
        response = await client.get(
            "/api/v1/films/?sort=-imdb_rating&page_size=10&page_number=1"
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 10
