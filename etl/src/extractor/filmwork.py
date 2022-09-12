import dataclasses as dtc
import datetime as dt
import logging
from collections import namedtuple
from typing import Set, Generator

from config import CONFIG
from state import FILM_STATE

from .base import BasePGExtractor

logger = logging.getLogger(__name__)

Person = namedtuple('Person', ['id', 'name'])
Genre = namedtuple('Genre', ['id', 'name'])


@dtc.dataclass(init=True)
class FilmworkRecord:
    fw_id: str
    title: str
    description: str
    rating: float
    type: str
    created_at: dt.datetime
    updated_at: dt.datetime
    min_access_level: int

    person_role: dtc.InitVar[str]
    person_id: dtc.InitVar[str]
    person_full_name: dtc.InitVar[str]
    genre_id: dtc.InitVar[str]
    genre_name: dtc.InitVar[str]

    directors: Set[Person] = dtc.field(default_factory=set)
    actors: Set[Person] = dtc.field(default_factory=set)
    writers: Set[Person] = dtc.field(default_factory=set)
    genres: Set[Genre] = dtc.field(default_factory=set)

    def place_person(self, person_role: str, person_id: str, person_full_name: str):
        person = Person(id=person_id, name=person_full_name)
        if person_role == 'writer':
            self.writers.add(person)
        elif person_role == 'actor':
            self.actors.add(person)
        elif person_role == 'director':
            self.directors.add(person)

    # pylint: disable=too-many-arguments
    def __post_init__(
            self,
            person_role: str,
            person_id: str,
            person_full_name: str,
            genre_id: str,
            genre_name: str
    ):
        self.place_person(person_role, person_id, person_full_name)
        genre = Genre(id=genre_id, name=genre_name)
        self.genres.add(genre)


class FilmWorkExtractor(BasePGExtractor):
    schema = CONFIG.extraction_schema.film
    state = FILM_STATE
    name = 'movies'

    def __init__(self, connection):
        super().__init__(connection, self.schema, self.state)

    @staticmethod
    def group_extracted(queryset) -> Generator[FilmworkRecord, None, int]:
        data_dict = {}
        for record in queryset:
            if record.fw_id in data_dict:
                data_dict[record.fw_id].place_person(record.person_role, record.person_id, record.person_full_name)
                data_dict[record.fw_id].genres.add(Genre(record.genre_id, record.genre_name))
            else:
                record_dict = record._asdict()
                data_dict[record.fw_id] = FilmworkRecord(**record_dict)
        for record in data_dict.values():
            yield record
