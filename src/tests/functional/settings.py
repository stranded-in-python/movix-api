from pydantic import BaseSettings, Field


class MoviesTestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    es_index: str = 'movies'
    es_id_field: str = ''

    service_url: str = 'http://127.0.0.1:9200'


test_settings = TestSettings()
