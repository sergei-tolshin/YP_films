from aiohttp import ClientSession
from core.exceptions import MovieNotFoundException
from core.settings import MOVIE_ID_URL, MOVIE_SEARCH_URL
from models.movie import Movie, MovieResponse


async def get_movie_id(client, title):
    headers = {'Accept': 'application/json'}
    params = {
        'query': title,
        'sort': '-relevance'
        }
    async with client.get(MOVIE_SEARCH_URL,
                          params=params,
                          headers=headers) as resp:
        if not resp.ok:
            raise MovieNotFoundException
        movies = await resp.json()
        return movies[0]['uuid']


async def get_movie_info(client, id):
    async with client.get(MOVIE_ID_URL + id) as resp:
        movie_info = await resp.json()
        return movie_info


async def movie_search(title):
    async with ClientSession() as client:
        movie_id = await get_movie_id(client, title)
        movie_info = await get_movie_info(client, movie_id)
        obj = MovieResponse(**movie_info)
        movie = Movie(id=str(obj.id), imdb_rating=obj.imdb_rating)
        await movie.create(obj, make_translate=False)
        return movie
