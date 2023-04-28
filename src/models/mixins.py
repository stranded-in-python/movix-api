from uuid import UUID

import orjson
from pydantic import BaseModel, validator

from core.utils import orjson_dumps


class JSONConfigMixin:
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UUIDMixin(BaseModel):
    id: UUID | str

    @validator('id')
    def string_to_float(cls, v):
        if v is str:
            return UUID(v)
        return v
