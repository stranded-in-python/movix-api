import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films
from core import config
from db import elastic, redis

app = FastAPI(
    title=config.settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = Redis(
        host=config.settings.redis_host, port=config.settings.redis_port
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"{config.settings.elastic_host}:{config.settings.elastic_port}"]
    )


@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()  # type: ignore


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=['/app']
    )
