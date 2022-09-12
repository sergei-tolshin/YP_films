from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    kafka_host: str = Field('localhost', env='ETL_KAFKA_HOST')
    kafka_port: str = Field('9092', env='ETL_KAFKA_PORT')
    kafka_topic: str = Field('movie_view_progress', env='KAFKA_TOPIC')
    clickhouse_host: str = Field('localhost', env='CLICKLHOUSE_HOST')
    clickhouse_port: int = Field('9000', env='CLICKLHOUSE_PORT')
    messages_count: int = Field('1000', env='MESSAGES_COUNT')
    max_timeout_batch: int = Field('60', env='MAX_TIMEOUT_BATCH')

    class Config:
        env_file = ".env"
