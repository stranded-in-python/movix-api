import pytest

from tests.test_services.testdata.films_responses import (
    FILM_DETAILED_SUCCESS,
    FILM_DETAILED_UNPROCESSABLE,
)

pytestmark = pytest.mark.asyncio


class TestFilm:
    async def test_get_by_id_ok(self, client):
        response = await client.get(
            "/api/v1/films/0312ed51-8833-413f-bff5-0e139c11264a"
        )
        assert response.status_code == 200, response.text
        assert response.json() == FILM_DETAILED_SUCCESS

    async def test_get_by_id_notfound(self, client):
        response = await client.get(
            "/api/v1/films/0311ed51-8833-413f-bff5-0e139c11264a"
        )
        assert response.status_code == 404, response.text

    async def test_get_by_id_unprocessable(self, client):
        response = await client.get("/api/v1/films/-1")
        assert response.status_code == 422, response.text
        assert response.json() == FILM_DETAILED_UNPROCESSABLE

    async def test_get_film_list(self, client):
        response = await client.get(
            "/api/v1/films/?sort=-imdb_rating&page_size=10&page_number=1"
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 10
