from unittest.mock import AsyncMock, MagicMock

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
async def test_get_manager_returns_instance(mocker, elastic_manager):
    mocked_get = mocker.patch.object(ElasticManager, "get_instance")
    mocked_get.return_value = elastic_manager
    manager = get_manager()
    assert manager == elastic_manager
    mocker.stopall()
