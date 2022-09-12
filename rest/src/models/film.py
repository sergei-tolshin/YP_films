from uuid import UUID

from pydantic import Field

from models.base import BaseOrJSONModel


class FilmPersonResponse(BaseOrJSONModel):
    """Nested person model for FilmResponse model."""

    id: UUID = Field(title="uuid", alias="uuid")
    name: str = Field(title="full_name", alias="full_name")

    class Config:
        allow_population_by_field_name = True


class FilmGenreResponse(BaseOrJSONModel):
    """Nested genre model for FilmResponse model."""

    id: UUID = Field(title="uuid", alias="uuid")
    name: str = Field(title="name")

    class Config:
        allow_population_by_field_name = True


class FilmResponse(BaseOrJSONModel):
    """Film model for response FastAPI."""

    id: UUID = Field(title="uuid", alias="uuid")
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list[FilmGenreResponse] | None
    actors: list[FilmPersonResponse] | None
    writers: list[FilmPersonResponse] | None
    directors: list[FilmPersonResponse] | None

    class Config:
        allow_population_by_field_name = True


class FilmListResponse(BaseOrJSONModel):
    """Films list model for response FastAPI."""

    id: UUID = Field(title="uuid", alias="uuid")
    title: str
    imdb_rating: float | None

    class Config:
        allow_population_by_field_name = True


class Film(BaseOrJSONModel):
    """Film model for data from ElasticSearch."""

    id: str
    imdb_rating: float | None
    title: str
    description: str | None
    actors_names: list[str] | None
    writers_names: list[str] | None
    directors_names: list[str] | None
    genres_names: list[str] | None
    genres: list[dict[str, str]] | None
    actors: list[dict[str, str]] | None
    writers: list[dict[str, str]] | None
    directors: list[dict[str, str]] | None
    min_access_level: int
