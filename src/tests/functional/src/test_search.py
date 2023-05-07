import pytest
from conftest import client, event_loop, test_app
from testdata.search_responses import *


@pytest.mark.asyncio
async def test_search_films_ok(client):
    response = await client.get(
        "/api/v1/films/search/?query=Star&page_number=1&page_size=2"
    )
    assert response.status_code == 200, response.text
    assert response.json() == SEARCH_FILMS_SUCCESS


@pytest.mark.asyncio
async def test_search_films_unprocessable(client):
    response = await client.get(
        "/api/v1/films/search/?query=Star&page_number=-1&page_size=2"
    )
    assert response.status_code == 422, response.text


@pytest.mark.asyncio
async def test_search_films_not_found(client):
    response = await client.get(
        "/api/v1/films/search/?query=jkngjrkt&page_number=1&page_size=2"
    )
    assert response.status_code == 404, response.text
    assert response.json() == SEARCH_FILMS_NOT_FOUND


@pytest.mark.asyncio
async def test_search_persons_ok(client):
    response = await client.get(
        "/api/v1/persons/search?query=Carrie&page_size=2&page_number=1"
    )
    assert response.status_code == 200, response.text
    assert response.json() == SEARCH_PERSONS_SUCCESS


@pytest.mark.asyncio
async def test_search_persons_unprocessable(client):
    response = await client.get(
        "/api/v1/persons/search?query=Carrie&page_size=-2&page_number=1"
    )
    assert response.status_code == 422, response.text


@pytest.mark.asyncio
async def test_search_persons_not_found(client):
    response = await client.get(
        "/api/v1/persons/search?query=ASJGNRIJGNRKJEG&page_size=2&page_number=1"
    )
    assert response.status_code == 404, response.text
    assert response.json() == SEARCH_PERSONS_NOT_FOUND
