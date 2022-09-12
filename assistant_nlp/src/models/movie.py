from typing import Optional
from uuid import UUID

from services.translate import Translate
from pydantic import Field

from models.base import BaseOrJSONModel


class MoviePersonResponse(BaseOrJSONModel):
    id: UUID = Field(title='uuid', alias='uuid')
    name: str = Field(title='full_name', alias='full_name')

    class Config:
        allow_population_by_field_name = True


class MovieGenreResponse(BaseOrJSONModel):
    id: UUID = Field(title='uuid', alias='uuid')
    name: str = Field(title='name')

    class Config:
        allow_population_by_field_name = True


class MovieInLang(BaseOrJSONModel):
    title: str
    description: str | None
    genres: str | None
    actors: str | None
    writers: str | None
    directors: str | None


class MovieResponse(BaseOrJSONModel):
    id: UUID = Field(title='uuid', alias='uuid')
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list[MovieGenreResponse] | None
    actors: list[MoviePersonResponse] | None
    writers: list[MoviePersonResponse] | None
    directors: list[MoviePersonResponse] | None

    class Config:
        allow_population_by_field_name = True


class MovieListResponse(BaseOrJSONModel):
    id: UUID = Field(title='uuid', alias='uuid')
    title: str
    imdb_rating: float or None

    class Config:
        allow_population_by_field_name = True


class Movie(BaseOrJSONModel):
    id: str = Field(title='uuid', alias='uuid')
    imdb_rating: float | None
    in_en: Optional[MovieInLang]
    in_ru: Optional[MovieInLang]
    is_translated: bool = False
    request_item: str | None

    class Config:
        allow_population_by_field_name = True

    def __lst_to_str(self, lst):
        return ', '.join(item.name for item in lst)

    async def create(self, data, make_translate: bool = True):
        genres = self.__lst_to_str(data.genres)
        actors = self.__lst_to_str(data.actors)
        writers = self.__lst_to_str(data.writers)
        directors = self.__lst_to_str(data.directors)
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
            tr = Translate()
            data_in_ru = await tr.translate(data_in_en, target_language='ru')
            self.in_ru = MovieInLang(
                **dict(zip(MovieInLang.__fields__.keys(), data_in_ru))
            )
            self.is_translated = True
