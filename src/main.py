import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis_manager = redis.get_manager()
    await redis_manager.on_startup()
    elastic_manager = elastic.get_manager()
    await elastic_manager.on_startup()


@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от баз при выключении сервера
    redis_manager = redis.get_manager()
    await redis_manager.on_shutdown()
    elastic_manager = elastic.get_manager()
    await elastic_manager.on_shutdown()  # type: ignore


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=['/app']
    )
