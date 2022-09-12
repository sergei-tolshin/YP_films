import random
from functools import lru_cache

from core.exceptions import NotFoundException
from core.utils.text import pluralize
from models.movie import Movie
from models.person import Person
from core.dialog.names import RESPONSE_RESULT

from services.search import MovieSearchService


class Handlers:
    def __init__(self, response, uo):
        self.uo = uo
        self.text = response.text
        self.params = response.parameters
        self.not_found = response.not_found
        self.no_data = response.no_data
        self.prompts = response.prompts
        self.response_variants = response.response_variants
        self.suggests = response.suggests
        self.search_client = MovieSearchService
        self.translate = True

    @property
    def _sess_movie(self):
        if movie := self.uo['session'].get('movie'):
            return Movie(**movie)
        return None

    @property
    def _sess_person(self):
        if person := self.uo['session'].get('person'):
            return Person(**person)
        return None

    async def _get_movie(self):
        if not self._sess_movie and self.params['movie_name']:
            try:
                movie = await self.search_client.movie_search(
                    title=self.params['movie_name'])
            except NotFoundException:
                movie = RESPONSE_RESULT.NOT_FOUND
        if self._sess_movie and self.params['movie_name']:
            if self._sess_movie.request_item == self.params['movie_name']:
                movie = self._sess_movie
            else:
                try:
                    movie = await self.search_client.movie_search(
                        title=self.params['movie_name'])
                except NotFoundException:
                    movie = RESPONSE_RESULT.NOT_FOUND
        if self._sess_movie and not self.params['movie_name']:
            movie = self._sess_movie
        if not self._sess_movie and not self.params['movie_name']:
            movie = RESPONSE_RESULT.UNKNOWN

        return movie

    async def _get_person(self):
        person_name = self.params.get('person_name', None)

        if not self._sess_person and person_name:
            try:
                person = await self.search_client.person_search(
                    name=person_name.get('name'))
            except NotFoundException:
                person = RESPONSE_RESULT.NOT_FOUND
        if self._sess_person and person_name:
            if self._sess_person.request_item == person_name.get('name'):
                person = self._sess_person
            else:
                try:
                    person = await self.search_client.person_search(
                        name=person_name.get('name'))
                except NotFoundException:
                    person = RESPONSE_RESULT.NOT_FOUND
        if self._sess_person and not person_name:
            person = self._sess_person
        if not self._sess_person and not person_name:
            person = RESPONSE_RESULT.UNKNOWN
        return person

    async def get_movie_search(self):
        movie = await self._get_movie()

        text = self.text.format(movie_name=movie.in_ru.title)

        self.uo['session']['movie'] = movie
        suggests = self.suggests
        return self.uo, text, suggests

    async def get_description(self):
        movie = await self._get_movie()

        if movie:
            description = movie.in_ru.description
            text = random.choice(self.no_data) if not description \
                else self.text.format(movie_description=description)
        elif movie == RESPONSE_RESULT.UNKNOWN:
            text = random.choice(self.prompts)
        else:
            text = random.choice(self.not_found)

        self.uo['session']['movie'] = movie
        suggests = self.suggests
        return self.uo, text, suggests

    async def get_genre(self):
        movie = await self._get_movie()

        if movie:
            genres = movie.in_ru.genres
            text = random.choice(self.no_data) if not genres \
                else self.text.format(genres=genres)
        elif movie == RESPONSE_RESULT.UNKNOWN:
            text = random.choice(self.prompts)
        else:
            text = random.choice(self.not_found)

        self.uo['session']['movie'] = movie
        suggests = self.suggests
        return self.uo, text, suggests

    async def get_rating(self):
        movie = await self._get_movie()

        if movie:
            rating = movie.imdb_rating
            text = random.choice(self.no_data) if not rating \
                else self.text.format(rating=rating)
        elif movie == RESPONSE_RESULT.UNKNOWN:
            text = random.choice(self.prompts)
        else:
            text = random.choice(self.not_found)

        self.uo['session']['movie'] = movie
        suggests = self.suggests
        return self.uo, text, suggests

    async def get_movie_persons(self):
        movie = await self._get_movie()

        if movie:
            person_type = self.params['person_type']
            match person_type:
                case "actor":
                    persons = movie.in_ru.actors
                case "director":
                    persons = movie.in_ru.directors
                case "writer":
                    persons = movie.in_ru.writers

            if persons:
                person = random.choice(persons.split(', '))

            text = random.choice(self.no_data) if not persons \
                else self.response_variants[person_type].format(
                    persons=persons, person=person)
        elif movie == RESPONSE_RESULT.UNKNOWN:
            text = random.choice(self.prompts)
        else:
            text = random.choice(self.not_found)

        self.uo['session']['movie'] = movie
        suggests = self.suggests
        return self.uo, text, suggests

    async def get_person_search(self):
        person = await self._get_person()
        person_type = self.params['person_type']

        text = self.response_variants[person_type].format(
            person=person.in_ru.name)

        self.uo['session']['person'] = person
        suggests = self.suggests
        return self.uo, text, suggests

    async def get_person_movies(self):
        person = await self._get_person()

        if person:
            movies = person.in_ru.best_movies
            text = random.choice(self.no_data) if not movies \
                else self.text.format(person=person.in_ru.name, movies=movies)
        elif person == RESPONSE_RESULT.UNKNOWN:
            text = random.choice(self.prompts)
        else:
            text = random.choice(self.not_found)

        self.uo['session']['person'] = person
        suggests = self.suggests
        return self.uo, text, suggests

    async def get_person_number_movies(self):
        person = await self._get_person()

        if person:
            person_type = self.params['person_type']

            match person_type:
                case "actor":
                    plural = pluralize(
                        person.number_movies, 'фильме,фильмах,фильмах')
                case "director":
                    plural = pluralize(
                        person.number_movies, 'фильм,фильма,фильмов')
                case "writer":
                    plural = pluralize(
                        person.number_movies, 'фильму,фильмам,фильмам')

            text = self.response_variants[person_type].format(
                person=person.in_ru.name,
                number=person.number_movies,
                plural=plural
            )
        elif person == RESPONSE_RESULT.UNKNOWN:
            text = random.choice(self.prompts)
        else:
            text = random.choice(self.not_found)

        self.uo['session']['person'] = person
        suggests = self.suggests
        return self.uo, text, suggests


@lru_cache()
def get_handlers() -> Handlers:
    return Handlers()
