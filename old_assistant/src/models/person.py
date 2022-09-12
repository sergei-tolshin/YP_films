from uuid import UUID

from models.base import BaseOrJSONModel


class Role(BaseOrJSONModel):
    """A role for parse"""

    role: str
    film_work_ids: list[str] | None


class PersonResponse(BaseOrJSONModel):
    """Person model for response FastAPI."""

    uuid: UUID
    full_name: str
    role: str or None
    film_ids: list[UUID] or None
