from uuid import UUID

import orjson
from pydantic import BaseModel, Field, validator

from core.utils import orjson_dumps


class JSONConfigMixin:
    json_loads = orjson.loads
    json_dumps = orjson_dumps


class UUIDMixin(BaseModel):
    id: UUID = Field(alias='uuid')

    @validator('id')
    def string_to_float(cls, v):
        if v is str:
            return UUID(v)
        return v

    class Config(JSONConfigMixin):
        allow_population_by_field_name = True
