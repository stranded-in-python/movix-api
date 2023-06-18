import os
from logging import config as logging_config

from pydantic import BaseSettings, SecretStr

from core.logger import LOG_LEVEL, get_logging_config


class ModelConfig:
    allow_population_by_field_name = True


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = 'movix-api'

    # Настройки Redis
    redis_host: str = 'redis'
    redis_port: int = 6379
    cache_expiration_in_seconds: int = 300

    # Настройки Elasticsearch
    elastic_endpoint: str = 'http://elastic:9200'

    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(__file__))

    log_level: str = LOG_LEVEL

    access_token_secret: SecretStr = SecretStr('ACCESS')
    access_token_audience: str = 'movix:auth'

    auth_user_rights_endpoint: str = 'http://auth:8000/api/v1/users/user_id/roles'


settings = Settings()


# Применяем настройки логирования
logging_config.dictConfig(get_logging_config(level=settings.log_level))
