from http import HTTPStatus

import pytest

import tests.test_services.testdata.genres_responses as test_responses

pytestmark = [pytest.mark.asyncio, pytest.mark.integrational]


class TestGenre:
    @pytest.mark.parametrize(
        'url,status_code,response_json',
        [
            (
                "/api/v1/genres/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
                HTTPStatus.OK,
                test_responses.GENRE_DETAILED_SUCCESS,
            ),
            (
                "/api/v1/genres/Action",
                HTTPStatus.UNPROCESSABLE_ENTITY,
                test_responses.GENRE_DETAILED_UNPROCESSABLE,
            ),
            (
                "/api/v1/genres/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07aa",
                HTTPStatus.NOT_FOUND,
                test_responses.GENRE_DETAILED_NOTFOUND,
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
        'url,status_code,count', [("/api/v1/genres", HTTPStatus.OK, 2)]
    )
    async def test_get_list(self, client, url, status_code, count):
        """Проверка получения списка жанров"""
        response = await client.get(url)
        response_list = response.json()

        assert response.status_code == status_code, response.text
        assert isinstance(response_list, list)
        assert len(response_list) != 0, len(response_list) <= 10
        assert len(response_list[0]) == count
        assert "name" in response_list[0], "uuid" in response_list[0]
