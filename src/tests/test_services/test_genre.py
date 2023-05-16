from http import HTTPStatus

import pytest

import tests.test_services.testdata.genres_responses as test_responses


class TestGenre:
    @pytest.mark.asyncio
    async def test_get_by_id_ok(self, client):
        """Проверка успешного получения информации о жанре
        по корректному идентификатору"""
        response = await client.get(
            "/api/v1/genres/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"
        )

        assert response.status_code == HTTPStatus.OK, response.text
        assert response.json() == test_responses.GENRE_DETAILED_SUCCESS

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, client):
        """Проверка обработки некорректного идентификатора жанра"""
        response = await client.get(
            "/api/v1/genres/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07aa"
        )

        assert response.status_code == HTTPStatus.NOT_FOUND, response.text
        assert response.json() == test_responses.GENRE_DETAILED_NOTFOUND

    @pytest.mark.asyncio
    async def test_get_by_id_unprocessable(self, client):
        response = await client.get("/api/v1/genres/Action")

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text
        assert response.json() == test_responses.GENRE_DETAILED_UNPROCESSABLE

    @pytest.mark.asyncio
    async def test_get_genre_list(self, client):
        """Проверка получения списка жанров"""
        response = await client.get("/api/v1/genres")
        assert response.status_code == HTTPStatus.OK, response.text

        response_list = response.json()
        assert isinstance(response_list, list)
        assert len(response_list) != 0, len(response_list) <= 10

        assert len(response_list[0]) == 2
        assert "name" in response_list[0], "uuid" in response_list[0]
