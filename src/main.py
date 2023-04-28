import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films
from core import config
from core.logger import LOGGING
from db import elastic, redis

app = FastAPI(
    title=config.settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis_manager = redis.get_manager()
    redis_manager.on_startup()
    elastic_manager = elastic.get_manager()
    elastic_manager.set_client(
        AsyncElasticsearch(
            hosts=[f"{config.settings.elastic_host}:{config.settings.elastic_port}"]
        )
    )


@app.on_event("shutdown")
async def shutdown():
    # Отключаемся от баз при выключении сервера
    redis_manager = redis.get_manager()
    await redis_manager.on_shutdown()
    elastic_manager = elastic.get_manager()
    await elastic_manager.on_shutdown()  # type: ignore


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=['/app']
    )
