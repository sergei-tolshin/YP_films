import os
from logging import config as logging_config
from pathlib import Path

import yaml
from core.logger import LOGGING
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent.absolute()

PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", "9200"))

TARGET_ENV = os.getenv("TARGET_ENV", "DEBUG")

RELOAD_ON_CHANGE = TARGET_ENV == "DEBUG"

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOGGING["loggers"][""]["level"] = LOG_LEVEL

DEFAULT_PAGE_SIZE = 100

logging_config.dictConfig(LOGGING)

MESSAGES_FILE_PATH = BASE_DIR / "core" / "messages.yml"


class MSG404(BaseModel):
    item: str
    list: str


class MSG403(BaseModel):
    item: str


class Response404(BaseModel):
    film: MSG404
    genre: MSG404
    person: MSG404


class Response403(BaseModel):
    film: MSG403


class Messages(BaseModel):
    not_found: Response404
    forbidden: Response403


with open(MESSAGES_FILE_PATH, encoding="utf-8") as config_file:
    data = yaml.load(config_file, Loader=yaml.Loader)
messages = Messages(**data)
