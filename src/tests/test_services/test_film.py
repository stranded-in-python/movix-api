from http import HTTPStatus

import pytest

from tests.test_services.testdata import films_responses

pytestmark = [pytest.mark.asyncio, pytest.mark.integrational]


class TestFilm:
    @pytest.mark.parametrize(
        'url,status_code,response_json',
        [
            (
                "/api/v1/films/0312ed51-8833-413f-bff5-0e139c11264a",
                HTTPStatus.OK,
                films_responses.FILM_DETAILED_SUCCESS,
            ),
            (
                "/api/v1/films/-1",
                HTTPStatus.UNPROCESSABLE_ENTITY,
                films_responses.FILM_DETAILED_UNPROCESSABLE,
            ),
            (
                "/api/v1/films/0311ed51-8833-413f-bff5-0e139c11264a",
                HTTPStatus.NOT_FOUND,
                films_responses.FILM_DETAILED_NOTFOUND,
            ),
        ],
    )
    async def test_get_details(self, client, url, status_code, response_json):
        response = await client.get(url)

        assert response.status_code == status_code, response.text
        assert response.json() == response_json

    @pytest.mark.parametrize(
        'url,status_code,count',
        [
            (
                "/api/v1/films/?sort=-imdb_rating&page_size=10&page_number=1",
                HTTPStatus.OK,
                10,
            )
        ],
    )
    async def test_get_film_list(self, client, url, status_code, count):
        response = await client.get(url)
        assert response.status_code == status_code, response.text
        assert len(response.json()) == count
