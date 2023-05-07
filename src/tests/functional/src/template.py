from fastapi.testclient import TestClient
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from db.elastic import ElasticClient, ElasticManager, get_manager
from main import app
from tests.test_db.test_elastic import elastic_manager as mock_elastic_manager, elastic_client as mock_elastic_client #mock\
from tests.test_db.test_redis import redis_manager as mock_redis_manager, redis_client as mock_redis_manager
from api.v1 import films

#По умолчанию их размещают в файле conftest.py Чтобы использовать фикстуру в тесте, нужно всего лишь указать её во входных параметрах.

test_app = app

@test_app.on_event("startup")
async def mock_startup():
    redis_manager = mock_redis_manager(mock_redis_manager())
    await redis_manager.on_startup()
    elastic_manager = mock_elastic_manager(mock_elastic_client())
    await elastic_manager.on_startup()

@test_app.on_event("shutdown")
async def mock_shutdown():
    redis_manager = mock_redis_manager(mock_redis_manager())
    await redis_manager.on_shutdown()
    elastic_manager = mock_elastic_manager(mock_elastic_client())
    await elastic_manager.on_shutdown()  # type: ignore

test_app.include_router(films.router, prefix="/api/v1/films", tags=["films"])

client = TestClient(test_app)

@pytest.mark.createuser
def test_create_user():
    response = client.get(
        "/api/v1/films/0312ed51-8833-413f-bff5-0e139c11264a"
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"uuid": "???"}

# 
# 



# для каждой группы ручек свой набор эндпоинтов

# if __name__ == "__main__":

#     test_create_user()