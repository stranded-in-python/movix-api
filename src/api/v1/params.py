from pydantic import BaseModel


class QueryParamMixin(BaseModel):
    page_size: int | None
    page_number: int | None


class QueryParamPersonName(QueryParamMixin):
    name: str


class QueryParamPersonId(QueryParamMixin):
    id: str
