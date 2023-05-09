import orjson
import pytest

import tests.functional.testdata.genres_responses as test_responses
from tests.functional.conftest import client, test_app


@pytest.mark.genre_detailed
async def test_get_by_id_ok(client):
    """Проверка успешного получения информации о жанре
    по корректному идентификатору"""
    response = await client.get("/api/v1/genres/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff")

    assert response.status_code == 200, response.text
    assert response.json() == test_responses.GENRE_DETAILED_SUCCESS


@pytest.mark.genre_detailed
async def test_get_by_id_not_found(client):
    """Проверка обработки некорректного идентификатора жанра"""
    response = await client.get("/api/v1/genres/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07aa")

    assert response.status_code == 404, response.text
    assert response.json() == test_responses.GENRE_DETAILED_NOTFOUND


@pytest.mark.genre_detailed
async def test_get_by_id_unprocessable(client):
    response = await client.get("/api/v1/genres/Action")

    assert response.status_code == 422, response.text
    assert response.json() == test_responses.GENRE_DETAILED_UNPROCESSABLE


@pytest.mark.genre_list
async def test_get_genre_list(client):
    """Проверка обработки некорректного идентификатора жанра"""
    response = await client.get("/api/v1/genres")
    assert response.status_code == 200, response.text

    response_list = response.json()
    assert isinstance(response_list, list)
    assert len(response_list) != 0, len(response_list) <= 10

    assert len(response_list[0]) == 2
    assert "name" in response_list[0], "uuid" in response_list[0]
