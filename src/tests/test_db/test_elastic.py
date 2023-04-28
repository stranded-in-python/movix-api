from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from db.elastic import ElasticClient, ElasticManager, get_manager


@pytest.fixture
def elastic_client():
    client = MagicMock(spec=ElasticClient)
    client.ping = AsyncMock()
    return client


@pytest.fixture
def elastic_manager(elastic_client):
    manager = ElasticManager(elastic_client)
    manager.on_startup = AsyncMock()
    manager.on_shutdown = AsyncMock()
    return manager


@pytest.mark.asyncio
async def test_elastic_client_ping(elastic_client):
    await elastic_client.ping()
    elastic_client.ping.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_manager_returns_instance(elastic_manager):
    with patch.object(ElasticManager, "get") as mocked_get:
        mocked_get.return_value = elastic_manager
        manager = await get_manager()
        assert manager == elastic_manager


def fake_init(self, *args, **kwargs):
    ...


@pytest.mark.asyncio
async def test_get_manager_creates_new_instance(elastic_manager, elastic_client):
    with (
        patch.object(ElasticManager, "get") as mocked_manager_get,
        patch.object(ElasticManager, "__new__") as mocked_manager_new,
        patch.object(ElasticClient, "__new__") as mocked_client_new,
    ):
        mocked_manager_get.return_value = None
        mocked_manager_new.return_value = elastic_manager
        mocked_client_new.return_value = elastic_client
        manager = await get_manager()
        assert manager == elastic_manager
