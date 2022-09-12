import abc
import logging
from functools import lru_cache
from elasticsearch import exceptions

from fastapi import Depends

from db.elastic import AsyncElasticProxy
from db.redis import AsyncRedisProxy
from db.base import AsyncDBProxy, AsyncCacheProxy
from models.genre import Genre
from .base import BaseCachedService

logger = logging.getLogger(__name__)


class GenreMethods(abc.ABC):

    @abc.abstractmethod
    async def get_list(self, page_size: int, page: int) -> list[Genre]:
        pass


class ElasticCachedGenreService(BaseCachedService, GenreMethods):
    model = Genre
    source = "genre"
    GenreBadRequestError = exceptions.RequestError

    async def get_list(self, page_size: int, page: int) -> list[Genre]:
        """
        Cached genres list.
        """
        body = {
            "size": page_size,
            "from": page_size * (page - 1),
            "query": {"match_all": {}},
        }
        return await self._search(body)


@lru_cache()
def get_genre_service(
    cache: AsyncCacheProxy = Depends(AsyncRedisProxy.create),
    db: AsyncDBProxy = Depends(AsyncElasticProxy.create),
) -> ElasticCachedGenreService:
    return ElasticCachedGenreService(cache, db)
