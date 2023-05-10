from asyncio import get_event_loop

import pytest
from httpx import AsyncClient

from main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_app():
    test_app = app

    yield test_app  # yield the application instance to the test function


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
