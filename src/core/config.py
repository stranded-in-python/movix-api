import os
from logging import config as logging_config

from pydantic import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = 'movies'

    # Настройки Redis
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    cache_expiration_in_seconds: int = 300

    # Настройки Elasticsearch
    elastic_endpoint: str = 'http://elastic:9200'

    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = Settings()
