import abc
import logging
from functools import lru_cache

from elasticsearch import exceptions
from fastapi import Depends

from db.base import AsyncCacheProxy, AsyncDBProxy
from db.elastic import AsyncElasticProxy
from db.redis import AsyncRedisProxy
from models.person import Person

from .base import BaseCachedService

logger = logging.getLogger(__name__)


class PersonMethods(abc.ABC):
    @abc.abstractmethod
    async def get_search(
        self, query: str, page_size: int, page: int, sort: str, order: str
    ) -> list[Person]:
        pass


class ElasticCachedPersonService(BaseCachedService, PersonMethods):
    model = Person
    source = "person"
    PersonBadRequestError = exceptions.RequestError

    async def get_search(
        self, query: str, page_size: int, page: int, sort: str, order: str
    ) -> list[Person]:
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
                    "fields": ["full_name"],
                    "operator": "and",
                }
            },
        }
        sort_arg = [{sort: {"order": order}}]
        return await self._search(body, sort_arg)


@lru_cache()
def get_person_service(
    cache: AsyncCacheProxy = Depends(AsyncRedisProxy.create),
    db: AsyncDBProxy = Depends(AsyncElasticProxy.create),
) -> ElasticCachedPersonService:
    return ElasticCachedPersonService(cache, db)
