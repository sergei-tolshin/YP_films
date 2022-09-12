from uuid import UUID

from models.base import BaseOrJSONModel


class Role(BaseOrJSONModel):
    """A role for parse"""

    role: str
    film_work_ids: list[str] | None


class Person(BaseOrJSONModel):
    """Person model for data from ElasticSearch."""

    id: str
    full_name: str
    roles: list[Role] | None


class PersonResponse(BaseOrJSONModel):
    """Person model for response FastAPI."""

    uuid: UUID
    full_name: str
    role: str | None
    film_ids: list[UUID] | None
