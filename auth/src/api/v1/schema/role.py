from uuid import UUID

from pydantic import Field

from .base import BaseOrJSONModel


class RoleResponseSchema(BaseOrJSONModel):
    uuid: UUID
    name: str = Field(regex="^[a-z0-9]+$", max_length=255)
    permission_level: int = Field(default=1)

    class Config:
        orm_mode = True
        extra = "ignore"
        validate_assignment = True


class RoleListResponseSchema(BaseOrJSONModel):
    roles: list[RoleResponseSchema]
    permission_level: int


class RoleRequestSchema(BaseOrJSONModel):
    name: str = Field(regex="^[a-z0-9]+$", max_length=255)
    permission_level: int = Field(default=1)


class RoleUpdateRequestSchema(BaseOrJSONModel):
    name: str | None = Field(regex="^[a-z0-9]+$", max_length=255)
    permission_level: int | None
