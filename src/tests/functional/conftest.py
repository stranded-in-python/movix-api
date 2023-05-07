from asyncio import get_event_loop

import pytest
# from fastapi.testclient import TestClient
from httpx import AsyncClient

from api.v1 import films, genres, persons
from main import app
from tests.test_db.test_elastic import elastic_client as mock_elastic_client
from tests.test_db.test_elastic import elastic_manager as mock_elastic_manager
from tests.test_db.test_redis import redis_client as mock_redis_manager
from tests.test_db.test_redis import redis_manager as mock_redis_manager


@pytest.fixture(scope="module")
def event_loop():
    loop = get_event_loop()
    yield loop


@pytest.fixture(scope="module")
async def test_app():
    test_app = app

    @app.on_event("startup")
    async def mock_startup():
        redis_manager = mock_redis_manager(mock_redis_manager())
        await redis_manager.on_startup()
        elastic_manager = mock_elastic_manager(mock_elastic_client())
        await elastic_manager.on_startup()

    @app.on_event("shutdown")
    async def mock_shutdown():
        redis_manager = mock_redis_manager(mock_redis_manager())
        await redis_manager.on_shutdown()
        elastic_manager = mock_elastic_manager(mock_elastic_client())
        await elastic_manager.on_shutdown()  # type: ignore

        test_app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
        test_app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
        test_app.include_router(
            persons.router, prefix="/api/v1/persons", tags=["persons"]
        )

    yield test_app  # yield the application instance to the test function


@pytest.fixture(scope="module")
async def client(test_app):
    async with AsyncClient(app=test_app, base_url="http://testserver") as client:
        yield client  # yield the client instance to the test function
