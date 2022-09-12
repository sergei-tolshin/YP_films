import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import Field, validator

from .base import BaseOrJSONModel


def convert_date_for_response_model(value: dt.date) -> str:
    return value.strftime("%Y-%m-%d")


def convert_datetime_for_response_model(value: dt.datetime) -> str:
    return value.isoformat()


class Pagination(BaseOrJSONModel):
    page: Optional[int]
    page_size: Optional[int]


class UserRequestSchema(BaseOrJSONModel):
    username: str = Field(regex="^[a-z0-9]+$", max_length=255)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    birth_date: dt.date
    email: str = Field(regex="(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    password: str = Field(max_length=512)


class UserUpdateRequestSchema(BaseOrJSONModel):
    username: str | None = Field(regex="^[a-z0-9]+$", max_length=255)
    first_name: str | None = Field(max_length=255)
    last_name: str | None = Field(max_length=255)
    birth_date: dt.date | None
    email: str | None = Field(
        regex="(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    )
    password: str | None = Field(max_length=512)


class UserResponseSchema(BaseOrJSONModel):
    uuid: UUID = Field(allow_mutation=False)
    username: str = Field(regex="^[a-z0-9]+$", max_length=255, allow_mutation=False)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    birth_date: dt.date
    email: str = Field(regex="(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    time_zone: int
    notification: bool

    _normalize_date = validator("birth_date", allow_reuse=True)(
        convert_date_for_response_model
    )

    class Config:
        orm_mode = True
        extra = "ignore"
        validate_assignment = True


class HistoryResponse(BaseOrJSONModel):
    timestamp: dt.datetime
    location: str | None
    device: str

    _normalize_date = validator("timestamp", allow_reuse=True)(
        convert_datetime_for_response_model
    )

    class Config:
        orm_mode = True
        extra = "ignore"
        validate_assignment = True


class HistoryListResponse(BaseOrJSONModel):
    history_list: list[HistoryResponse]
