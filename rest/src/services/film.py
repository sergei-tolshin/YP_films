import abc
import logging
from functools import lru_cache

import aiohttp
import elasticsearch as es
from fastapi import Depends, Cookie, HTTPException, status, Header

from core.config import messages
from db.base import AsyncCacheProxy, AsyncDBProxy
from db.elastic import AsyncElasticProxy
from db.redis import AsyncRedisProxy
from models.film import Film
from services.base import BaseCachedService

logger = logging.getLogger(__name__)


class FilmMethods(abc.ABC):
    @abc.abstractmethod
    async def get_list(
            self, sort: str, page_size: int, page: int, filter_genre: str, order: str
    ) -> list[Film]:
        pass

    @abc.abstractmethod
    async def get_search(
            self, query: str, sort: str, page_size: int, page: int, order: int
    ) -> list[Film]:
        pass

    @abc.abstractmethod
    async def get_films_by_person(self, person_id: str) -> list[Film]:
        pass


class ElasticCachedFilmService(BaseCachedService, FilmMethods):
    model = Film
    source = "movies"
    FilmBadRequestError = es.exceptions.RequestError

    async def get_list(
            self, sort: str, page_size: int, page: int, filter_genre: str, order: str
    ) -> list[Film]:
        """
        Function to get all films in Elastic with sorting and filtering.
        First check cache, then search in Elastic and
        put in cache.
        """
        if not filter_genre:
            body = {
                "size": page_size,
                "from": page_size * (page - 1),
                "query": {"match_all": {}},
            }
        else:
            body = {
                "size": page_size,
                "from": page_size * (page - 1),
                "query": {
                    "nested": {
                        "path": "genres",
                        "query": {"match": {"genres.id": filter_genre}},
                    }
                },
            }
        sort_arg = [{sort: {"order": order}}]
        return await self._search(query=body, sort=sort_arg)

    async def get_search(
            self, query: str, sort: str, page_size: int, page: int, order: int
    ) -> list[Film]:
        """
        Cached search query.
        """
        body = {
            "size": page_size,
            "from": page_size * (page - 1),
            "query": {
                "multi_match": {
                    "query": query,
                    "type": "best_fields",
                    "fuzziness": "auto",
                    "fields": ["title^2", "description"],
                    "operator": "and",
                }
            },
        }
        sort_arg = [{sort: {"order": order}}]
        return await self._search(query=body, sort=sort_arg)

    async def get_films_by_person(self, person_id: str) -> list[Film]:
        body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"match": {"actors.id": person_id}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"match": {"writers.id": person_id}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"match": {"directors.id": person_id}},
                            }
                        },
                    ]
                }
            }
        }
        return await self._search(
            query=body,
        )


@lru_cache()
def get_film_service(
        cache: AsyncCacheProxy = Depends(AsyncRedisProxy.create),
        db: AsyncDBProxy = Depends(AsyncElasticProxy.create),
) -> ElasticCachedFilmService:
    """Function to get connections with Redis and ElasticSearch."""
    return ElasticCachedFilmService(cache, db)


async def get_min_permission_level(
        access_token_cookie: str | None = Cookie(None),
        refresh_token_cookie: str | None = Cookie(None),
        x_request_id: str | None = Header(None)
):
    if not access_token_cookie or not refresh_token_cookie:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=messages.forbidden.film.item)
    async with aiohttp.ClientSession(
            cookies={"access_token_cookie": access_token_cookie, "refresh_token_cookie": refresh_token_cookie}
    ) as session:
        async with session.get(
                'http://auth-rest:5000/inside_api/get-permission-level',
                headers={"X-Request-Id": x_request_id},
                json={}
        ) as response:
            data = await response.json()
            if not data:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail=messages.forbidden.film.item)
            return data
