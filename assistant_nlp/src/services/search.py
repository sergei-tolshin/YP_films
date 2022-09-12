from operator import itemgetter

from aiohttp import ClientSession
from core.config import settings
from core.exceptions import NotFoundException
from models.movie import Movie, MovieResponse
from models.person import Person

from services.translate import Translate


class MovieSearch:
    def __init__(self, make_translate: bool = True) -> None:
        self.client = ClientSession
        self.headers = {'Content-Type': 'application/json'}
        self.translate = make_translate
        self.translate_client = Translate().translate

    async def _set_params(self, query: str):
        return {'query': query, 'sort': '-relevance'}

    async def _get_movie_id(self, client, title: str):
        async with client.get(settings.SEARCH_APP_MOVIE_SEARCH_URL,
                              params=await self._set_params(title),
                              headers=self.headers) as resp:
            if not resp.ok:
                raise NotFoundException
            movies = await resp.json()
        return movies[0]['uuid']

    async def _get_movie_info(self, client, id: str):
        async with client.get(settings.SEARCH_APP_MOVIE_ID_URL.format(id=id)) as resp:
            movie_info = await resp.json()
        return movie_info

    async def _get_person(self, client, name: str):
        async with client.get(settings.SEARCH_APP_PERSON_SEARCH_URL,
                              params=await self._set_params(name),
                              headers=self.headers) as resp:
            if not resp.ok:
                raise NotFoundException
            persons = await resp.json()
        return persons[0]

    async def _get_person_movies(self, client, id: str):
        async with client.get(settings.SEARCH_APP_PERSON_ID_URL.format(id=id)) as resp:
            movies = await resp.json()
        return movies

    async def movie_search(self, title: str):
        if self.translate:
            title = await self.translate_client(title, one_item=True)

        async with self.client() as client:
            movie_id = await self._get_movie_id(client, title)
            movie_info = await self._get_movie_info(client, movie_id)
        obj = MovieResponse(**movie_info)
        movie = Movie(
            id=str(obj.id),
            imdb_rating=obj.imdb_rating,
            request_item=title
        )
        await movie.create(obj, make_translate=self.translate)
        return movie

    async def person_search(self, name: str, num_movies: int = 5):
        if self.translate:
            name = await self.translate_client(name, one_item=True)

        async with self.client() as client:
            person = await self._get_person(client, name)
            movies = await self._get_person_movies(client, person['uuid'])
        number_movies = len(movies)
        sorted_movies = sorted(
            movies,
            key=itemgetter('imdb_rating'),
            reverse=True
        )
        person_obj = Person(
            id=str(person['uuid']),
            number_movies=number_movies,
            request_item=name
        )
        await person_obj.create(
            person['full_name'],
            sorted_movies[:num_movies],
            make_translate=self.translate
        )
        return person_obj


MovieSearchService = MovieSearch(make_translate=True)
