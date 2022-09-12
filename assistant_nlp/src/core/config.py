from logging import config as logging_config
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, HttpUrl

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = 'assistant_app'

    # Корень проекта
    BASE_DIR: Optional[Path] = BASE_DIR

    # Dialogflow
    DIALOGFLOW_PROJECT_ID: str = 'assistant-hwuy'
    DIALOGFLOW_LANGUAGE_CODE: str = 'ru'

    # Сервис поиска фильмов
    SEARCH_APP_URL: HttpUrl = 'http://127.0.0.1:8000'
    SEARCH_APP_API_URL: HttpUrl = f"{SEARCH_APP_URL}/api/v1"

    SEARCH_APP_MOVIE_URL: HttpUrl = f"{SEARCH_APP_API_URL}/film"
    SEARCH_APP_MOVIE_SEARCH_URL: HttpUrl = f"{SEARCH_APP_MOVIE_URL}/search"
    SEARCH_APP_MOVIE_ID_URL: HttpUrl = f"{SEARCH_APP_MOVIE_URL}/{{id}}"

    SEARCH_APP_PERSON_URL: HttpUrl = f"{SEARCH_APP_API_URL}/person"
    SEARCH_APP_PERSON_SEARCH_URL: HttpUrl = f"{SEARCH_APP_PERSON_URL}/search"
    SEARCH_APP_PERSON_ID_URL: HttpUrl = f"{SEARCH_APP_PERSON_URL}/{{id}}/film"

    # Переводчик
    TRANSLATE_URL: HttpUrl = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    TRANSLATE_TOKEN: str = ''

    class Config:
        env_file = '.env'


settings = Settings()
