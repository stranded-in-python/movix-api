import pytest

from db.abc import Singleton


@pytest.fixture(autouse=True)
def reset_singleton(mocker):
    mocker.patch.dict(Singleton._instances, clear=True)
