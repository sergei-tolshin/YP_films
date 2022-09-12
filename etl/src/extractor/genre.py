import dataclasses as dtc
import datetime as dt
from collections import namedtuple
from typing import Generator, NamedTuple
import logging

from config import CONFIG
from state import GENRE_STATE

from .base import BasePGExtractor


logger = logging.getLogger(__name__)

FilmWork = namedtuple('FilmWork', ['id', 'imdb_rating'])


@dtc.dataclass(init=True)
class GenreRecord:
    g_id: str
    name: str
    created_at: dt.datetime
    updated_at: dt.datetime


class GenreExtractor(BasePGExtractor):

    schema = CONFIG.extraction_schema.genre
    state = GENRE_STATE
    name = 'genre'

    def __init__(self, connection):
        super().__init__(connection, self.schema, self.state)

    @staticmethod
    def group_extracted(queryset: Generator[NamedTuple, None, None]) -> Generator[GenreRecord, None, int]:
        for record in queryset:
            record_dict = record._asdict()
            yield GenreRecord(**record_dict)
