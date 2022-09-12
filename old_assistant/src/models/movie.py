from typing import Optional
from uuid import UUID

from core.utils import translate
from pydantic import Field

from models.base import BaseOrJSONModel


class MoviePersonResponse(BaseOrJSONModel):
    """Nested person model for MovieResponse model."""

    id: UUID = Field(title="uuid", alias="uuid")
    name: str = Field(title="full_name", alias="full_name")

    class Config:
        allow_population_by_field_name = True


class MovieGenreResponse(BaseOrJSONModel):
    """Nested genre model for MovieResponse model."""

    id: UUID = Field(title="uuid", alias="uuid")
    name: str = Field(title="name")

    class Config:
        allow_population_by_field_name = True


class MovieInLang(BaseOrJSONModel):
    title: str
    description: str
    genres: str
    actors: str
    writers: str
    directors: str


class MovieResponse(BaseOrJSONModel):
    """Movie model for response FastAPI."""

    id: UUID = Field(title="uuid", alias="uuid")
    title: str
    imdb_rating: float or None
    description: str or None
    genres: list[MovieGenreResponse] or None
    actors: list[MoviePersonResponse] or None
    writers: list[MoviePersonResponse] or None
    directors: list[MoviePersonResponse] or None

    class Config:
        allow_population_by_field_name = True


class MovieListResponse(BaseOrJSONModel):
    """Movie list model for response FastAPI."""

    id: UUID = Field(title="uuid", alias="uuid")
    title: str
    imdb_rating: float or None

    class Config:
        allow_population_by_field_name = True


class Movie(BaseOrJSONModel):
    id: str = Field(title="uuid", alias="uuid")
    imdb_rating: float or None
    in_en: Optional[MovieInLang]
    in_ru: Optional[MovieInLang]
    is_translated: bool = False

    class Config:
        allow_population_by_field_name = True

    async def create(self, data, make_translate: bool = True):
        genres = ', '.join(_.name for _ in data.genres)
        actors = ', '.join(_.name for _ in data.actors)
        writers = ', '.join(_.name for _ in data.writers)
        directors = ', '.join(_.name for _ in data.directors)
        data_in_en = [
            data.title,
            data.description,
            genres,
            actors,
            writers,
            directors
        ]
        self.in_en = MovieInLang(
                **dict(zip(MovieInLang.__fields__.keys(), data_in_en))
            )

        if not self.is_translated and make_translate:
            data_in_ru = await translate(data_in_en, target_language='ru')
            self.in_ru = MovieInLang(
                **dict(zip(MovieInLang.__fields__.keys(), data_in_ru))
            )
            self.is_translated = True
