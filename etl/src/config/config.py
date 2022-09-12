from os import environ
from pathlib import Path
from typing import Optional, List, Tuple

import yaml
from pydantic import BaseSettings, Field, BaseModel
from pydantic.env_settings import SettingsSourceCallable

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE_PATH = environ.get('ETL_CONFIG_FILE', 'src/config/default.yml')


class EnvPrioritySettings(BaseSettings):

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


class DSNSettings(EnvPrioritySettings):
    host: str = Field(..., env='POSTGRES_HOST')
    port: str = Field(..., env='POSTGRES_PORT')
    dbname: str = Field(..., env='POSTGRES_DB')
    password: str = Field(..., env='POSTGRES_PASSWORD')
    user: str = Field(..., env='POSTGRES_USER')


class PostgresSettings(BaseSettings):
    dsn: DSNSettings
    sql_folder: str = 'sql_templates'


class RelatedTable(BaseModel):
    table_name: str
    relations_table: str
    related_id: str
    updated_id: str


class QueryTemplates(BaseModel):
    related: str
    updated: str
    extract: str


class IndexExtractSchema(BaseSettings):
    limit: Optional[int] = 100
    main_extraction_table: str
    query_templates: QueryTemplates
    related_tables: Optional[List[RelatedTable]]


class ExtractionSchema(BaseSettings):
    film: IndexExtractSchema
    genre: IndexExtractSchema
    person: IndexExtractSchema


class ElasticSettings(EnvPrioritySettings):
    host: str = Field(..., env='ELASTIC_HOST')
    port: str = Field(..., env='ELASTIC_PORT')


class ETLConfig(BaseSettings):
    pg: PostgresSettings
    elastic: ElasticSettings
    extraction_schema: ExtractionSchema
    fetch_delay: float = 0.2
    state_file_dir: Optional[Path] = BASE_DIR
    extract_duration: int = 5


def load_config(config_fname: str = CONFIG_FILE_PATH) -> ETLConfig:
    with open(config_fname, encoding='utf-8') as config_file:
        config_data = yaml.load(config_file, Loader=yaml.SafeLoader)
    config = ETLConfig(**config_data)
    return config
