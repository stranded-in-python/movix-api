from http import HTTPStatus

import pytest

import tests.test_services.testdata.person_responses as test_responses

pytestmark = pytest.mark.asyncio


class TestPerson:
    async def test_get_by_id_ok(self, client):
        """Проверка успешного получения информации
        о персоне по корректному идентификатору"""
        response = await client.get(
            "/api/v1/persons/5b4bf1bc-3397-4e83-9b17-8b10c6544ed1"
        )

        assert response.status_code == HTTPStatus.OK, response.text
        assert response.json() == test_responses.PERSON_DETAILED_SUCCESS

    async def test_get_by_id_not_found(self, client):
        """Проверка обработки несуществующего идентификатора персоны"""
        response = await client.get(
            "/api/v1/persons/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"
        )

        assert response.status_code == HTTPStatus.NOT_FOUND, response.text
        assert response.json() == test_responses.PERSON_DETAILED_NOTFOUND

    async def test_get_by_id_unprocessable(self, client):
        """Проверка обработки некорректного формата
        идентификатора персоны"""
        response = await client.get("/api/v1/persons/HarrisonFord")

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text
        assert response.json() == test_responses.PERSON_DETAILED_UNPROCESSABLE

    async def test_get_person_films_ok(self, client):
        """Проверка успешного получения списка фильмов персоны"""
        response = await client.get(
            "/api/v1/persons/5b4bf1bc-3397-4e83-9b17-8b10c6544ed1/film"
        )
        assert response.status_code == HTTPStatus.OK, response.text

        response_list = response.json()
        assert isinstance(response_list, list)
        assert len(response_list) != 0, len(response_list) <= 10

        assert len(response_list[0]) == 3
        assert "uuid" in response_list[0]
        assert "title" in response_list[0]
        assert "imdb_rating" in response_list[0]

    async def test_get_person_films_not_found_person(self, client):
        """Проверка обработки несуществующего идентификатора персоны"""
        response = await client.get(
            "/api/v1/persons/00000000-0000-0000-0000-000000000000/film"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, response.text
        assert response.json() == test_responses.PERSON_DETAILED_NOTFOUND

    async def test_get_person_films_unprocessable_person_id(self, client):
        """Проверка обработки некорректного формата
        идентификатора персоны"""
        response = await client.get("/api/v1/persons/HarrisonFord/film")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text
        assert response.json() == test_responses.PERSON_DETAILED_UNPROCESSABLE

    async def test_search_person_ok(self, client):
        """Проверка успешного поиска по персонам"""
        response = await client.get("/api/v1/persons/search?query=Harrison%20Ford")
        assert response.status_code == HTTPStatus.OK, response.text

        response_list = response.json()
        assert isinstance(response_list, list)
        assert len(response_list) != 0, len(response_list) <= 10

        assert len(response_list[0]) == 3
        assert "uuid" in response_list[0]
        assert "full_name" in response_list[0]
        assert "films" in response_list[0]

        assert "uuid" in response_list[0]["films"][0]
        assert "title" in response_list[0]["films"][0]
        assert "imdb_rating" in response_list[0]["films"][0]
        assert "roles" in response_list[0]["films"][0]

    async def test_search_person_not_found(self, client):
        """Проверка обработки пустого результата поиска:"""
        response = await client.get("/api/v1/persons/search?query=NOTFOUNDPERSON")
        assert response.status_code == HTTPStatus.NOT_FOUND, response.text
        assert response.json() == {'detail': 'persons not found'}
