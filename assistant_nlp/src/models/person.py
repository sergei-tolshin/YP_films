from typing import Optional
from uuid import UUID

from services.translate import Translate
from pydantic import Field

from models.base import BaseOrJSONModel


class Role(BaseOrJSONModel):
    """A role for parse"""

    role: str
    film_work_ids: list[str] or None


class PersonResponse(BaseOrJSONModel):
    """Person model for response FastAPI."""

    uuid: UUID
    full_name: str
    role: str or None
    film_ids: list[UUID] or None


class PersonInLang(BaseOrJSONModel):
    name: str
    best_movies: str | None


class Person(BaseOrJSONModel):
    id: str = Field(title='uuid', alias='uuid')
    number_movies: int | None
    in_en: Optional[PersonInLang]
    in_ru: Optional[PersonInLang]
    is_translated: bool = False
    request_item: str | None

    class Config:
        allow_population_by_field_name = True

    async def create(self, name, data, make_translate: bool = True):
        best_movies = ', '.join(movie['title'] for movie in data)
        data_in_en = [name, best_movies]
        self.in_en = PersonInLang(
                **dict(zip(PersonInLang.__fields__.keys(), data_in_en))
            )

        if not self.is_translated and make_translate:
            tr = Translate()
            data_in_ru = await tr.translate(data_in_en, target_language='ru')
            self.in_ru = PersonInLang(
                **dict(zip(PersonInLang.__fields__.keys(), data_in_ru))
            )
            self.is_translated = True
