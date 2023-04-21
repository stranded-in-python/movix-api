from uuid import UUID

import orjson
from pydantic import BaseModel

from core.utils import orjson_dumps


class JSONConfigMixin:
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UUIDMixin(BaseModel):
    uuid: UUID
