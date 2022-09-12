from uuid import UUID

from pydantic import Field

from models.base import BaseOrJSONModel


class Genre(BaseOrJSONModel):
    """Genre model for data from ElasticSearch."""

    id: str
    name: str


class GenreResponse(BaseOrJSONModel):
    """Person model for response FastAPI."""

    id: UUID = Field(title="uuid", alias="uuid")
    name: str

    class Config:
        allow_population_by_field_name = True
