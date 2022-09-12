from uuid import UUID

from flask_pydantic_spec import FlaskPydanticSpec
from pydantic import BaseModel


spec = FlaskPydanticSpec('flask', title="Auth-Service", version="v1.0")


class BaseResponseSchema(BaseModel):
    msg: str


class UUUIDRequestSchema(BaseModel):
    uuid: UUID
