from functools import lru_cache
from uuid import UUID

from db.elastic import get_manager as get_elastic_manager
from models.models import PersonShort
from storages.abc import PersonStorageABC
from storages.storages import PersonElasticStorage

from .abc import PersonServiceABC


class PersonService(PersonServiceABC):
    def __init__(self, storage: PersonStorageABC):
        self.storage = storage

    async def get_by_id(self, item_id: UUID) -> PersonShort | None:
        """Данные по персоне."""
        return await self.storage.get_item(item_id)

    async def get_by_query(self, name: str, pagination_params) -> list[PersonShort]:
        """Поиск по персонам."""
        return await self.storage.get_items(name, pagination_params)


@lru_cache
def get_persons_service() -> PersonService:
    return PersonService(storage=PersonElasticStorage(get_elastic_manager))
