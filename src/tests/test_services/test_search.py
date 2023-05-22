from http import HTTPStatus

import pytest

from tests.test_services.testdata import search_responses

pytestmark = [pytest.mark.asyncio, pytest.mark.integrational]


class TestSearch:
    @pytest.mark.parametrize(
        'url,status_code,response_json',
        [
            (
                "/api/v1/films/search/?query=Star&page_number=1&page_size=2",
                HTTPStatus.OK,
                search_responses.SEARCH_FILMS_SUCCESS,
            ),
            (
                "/api/v1/films/search/?query=Star&page_number=-1&page_size=2",
                HTTPStatus.UNPROCESSABLE_ENTITY,
                search_responses.SEARCH_FILMS_UNPROCESSABLE_PAGE_NUMBER,
            ),
            (
                "/api/v1/films/search/?query=jkngjrkt&page_number=1&page_size=2",
                HTTPStatus.NOT_FOUND,
                search_responses.SEARCH_FILMS_NOT_FOUND,
            ),
            (
                "/api/v1/persons/search?query=Carrie&page_size=2&page_number=1",
                HTTPStatus.OK,
                search_responses.SEARCH_PERSONS_SUCCESS,
            ),
            (
                "/api/v1/persons/search?query=Carrie&page_size=-2&page_number=1",
                HTTPStatus.UNPROCESSABLE_ENTITY,
                search_responses.SEARCH_PERSONS_UNPROCESSABLE_PAGE_SIZE,
            ),
            (
                "/api/v1/persons/search?query=ASJGNRIJGNRKJEG&page_size=2&page_number=1",
                HTTPStatus.NOT_FOUND,
                search_responses.SEARCH_PERSONS_NOT_FOUND,
            ),
        ],
    )
    async def test_search(self, client, url, status_code, response_json):
        response = await client.get(url)
        assert response.status_code == status_code, response.text
        assert response.json() == response_json
