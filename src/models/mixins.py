import orjson
from pydantic import BaseModel
from uuid import UUID

from src.core.utils import orjson_dumps


class JSONConfigMixin:
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UUIDMixin(BaseModel):
    uuid: UUID
