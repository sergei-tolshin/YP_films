import abc
import json
import logging
from functools import wraps
from typing import Any, Type
from uuid import UUID

from db.base import AsyncCacheProxy, AsyncDBProxy
from models.base import BaseOrJSONModel

logger = logging.getLogger(__name__)


class BaseService(abc.ABC):
    source: str
    model: Type[BaseOrJSONModel]

    @abc.abstractmethod
    async def get(
        self, id_: UUID
    ) -> BaseOrJSONModel | None:
        pass

    @abc.abstractmethod
    async def _search(
        self, query: dict, sort: list | None = None, model=None
    ) -> BaseOrJSONModel | None:
        pass


class BaseCachedService(BaseService):
    def __init__(self, cache: AsyncCacheProxy, db: AsyncDBProxy):
        self._cache = cache
        self._db = db

    @staticmethod
    def cache_wrap(func):
        """Decorator for get and put film in redis."""

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # pylint: disable=protected-access
            cache_key = (
                type(self).__name__
                + "_"
                + func.__name__
                + "_"
                + "_".join(
                    f"{i}_{j}" for i, j in zip(func.__code__.co_varnames[1:], args) if j
                )
                + "_".join(f"{k}_{v}" for k, v in kwargs.items())
            )
            docs = await self._cache.get(cache_key, model=self.model)
            if not docs:
                docs = await func(self, *args, **kwargs)
                if not docs:
                    return None
                await self._cache.put(
                    cache_key,
                    json.dumps([doc.dict() for doc in docs])
                    if isinstance(docs, list)
                    else docs.json(),
                )
            return docs

        return wrapper

    @cache_wrap
    async def get(self, id_: str) -> BaseOrJSONModel | None:
        return await self._db.get(self.source, id_, self.model)

    @cache_wrap
    async def _search(
        self, query: dict, sort: list | None = None, model=None
    ) -> list[BaseOrJSONModel] | None:
        if model is None:
            model = self.model
        return await self._db.search(self.source, query, model, sort)


def get_search_body(query: str, page_size: int, page: int) -> dict[str, Any]:
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
    return body
