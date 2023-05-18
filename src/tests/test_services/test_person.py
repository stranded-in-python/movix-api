from http import HTTPStatus

import pytest

import tests.test_services.testdata.person_responses as test_responses

pytestmark = pytest.mark.asyncio


class TestPerson:
    @pytest.mark.parametrize(
        'url,status_code,response_json',
        [
            (
                "/api/v1/persons/5b4bf1bc-3397-4e83-9b17-8b10c6544ed1",
                HTTPStatus.OK,
                test_responses.PERSON_DETAILED_SUCCESS,
            ),
            (
                "/api/v1/persons/HarrisonFord/film",
                HTTPStatus.UNPROCESSABLE_ENTITY,
                test_responses.PERSON_DETAILED_UNPROCESSABLE,
            ),
            (
                "/api/v1/persons/00000000-0000-0000-0000-000000000000/film",
                HTTPStatus.NOT_FOUND,
                test_responses.PERSON_DETAILED_NOTFOUND,
            ),
            (
                "/api/v1/persons/search?query=NOTFOUNDPERSON",
                HTTPStatus.NOT_FOUND,
                {'detail': 'persons not found'},
            ),
        ],
    )
    async def test_get_by_id(self, client, url, status_code, response_json):
        """Проверка успешного получения информации о жанре
        по корректному идентификатору"""
        response = await client.get(url)

        assert response.status_code == status_code, response.text
        assert response.json() == response_json

    @pytest.mark.parametrize(
        'url,status_code,count',
        [
            (
                "/api/v1/persons/5b4bf1bc-3397-4e83-9b17-8b10c6544ed1/film",
                HTTPStatus.OK,
                3,
            )
        ],
    )
    async def test_get_film_list(self, client, url, status_code, count):
        """Проверка получения списка жанров"""
        response = await client.get(url)
        response_list = response.json()

        assert response.status_code == status_code, response.text
        assert isinstance(response_list, list)
        assert len(response_list) != 0, len(response_list) <= 10
        assert len(response_list[0]) == count
        assert "uuid" in response_list[0]
        assert "title" in response_list[0]
        assert "imdb_rating" in response_list[0]

    @pytest.mark.parametrize(
        'url,status_code,count',
        [("/api/v1/persons/search?query=Harrison%20Ford", HTTPStatus.OK, 3)],
    )
    async def test_search(self, client, url, status_code, count):
        """Проверка успешного поиска по персонам"""
        response = await client.get(url)
        response_list = response.json()

        assert response.status_code == status_code, response.text
        assert isinstance(response_list, list)
        assert len(response_list) != 0, len(response_list) <= 10
        assert len(response_list[0]) == count

        assert "uuid" in response_list[0]
        assert "full_name" in response_list[0]
        assert "films" in response_list[0]

        assert "uuid" in response_list[0]["films"][0]
        assert "title" in response_list[0]["films"][0]
        assert "imdb_rating" in response_list[0]["films"][0]
        assert "roles" in response_list[0]["films"][0]
