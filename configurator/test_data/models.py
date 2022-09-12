import dataclasses as dc
import datetime as dt
from uuid import UUID

# pylint: disable=too-many-instance-attributes


@dc.dataclass
class GenreRecord:
    id: UUID
    name: str
    description: str
    created_at: dt.datetime
    updated_at: dt.datetime


@dc.dataclass
class PersonRecord:
    id: UUID
    full_name: str
    birth_date: dt.date
    created_at: dt.datetime
    updated_at: dt.datetime


@dc.dataclass
class FilmWorkRecord:
    id: UUID
    title: str
    description: str
    creation_date: dt.date
    certificate: str
    file_path: str
    rating: float
    type: str
    created_at: dt.datetime
    updated_at: dt.datetime
    min_access_level: int


@dc.dataclass
class GenreFilmWorkRecord:
    id: UUID
    film_work_id: UUID
    genre_id: UUID
    created_at: dt.datetime


@dc.dataclass
class PersonFilmWorkRecord:
    id: UUID
    film_work_id: UUID
    person_id: UUID
    role: str
    created_at: dt.datetime


ALL_DATA = (
    ('film_work', FilmWorkRecord),
    ('genre', GenreRecord),
    ('person', PersonRecord),
    ('genre_film_work', GenreFilmWorkRecord),
    ('person_film_work', PersonFilmWorkRecord),
)
