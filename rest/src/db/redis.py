import logging
import json
from typing import Type

import aioredis

from core import config
from db.base import AsyncCacheProxy
from models.base import BaseOrJSONModel

logger = logging.getLogger(__name__)
redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    return redis


class AsyncRedisProxy(AsyncCacheProxy):
    def __init__(self):
        self._redis = None

    @classmethod
    async def create(cls):
        instance = cls()
        instance._redis = await get_redis()
        return instance

    async def put(self, key: str, data: object):
        await self._redis.set(key, data, ex=config.FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get(
        self, key: str, model: Type[BaseOrJSONModel]
    ) -> BaseOrJSONModel | list[BaseOrJSONModel] | None:
        """Function to get data from cache by the key. Returns the class model object."""
        try:
            raw_data = await self._redis.get(key)
        except aioredis.exceptions.ConnectionError:
            raw_data = None
            logger.error("redis cache unavailable")
        if not raw_data:
            return None
        data = json.loads(raw_data)

        if isinstance(data, list):
            items = [model(**item) for item in data]
            return items

        item = model(**data)
        return item
