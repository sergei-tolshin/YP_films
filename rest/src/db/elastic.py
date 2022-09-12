import logging
from typing import Type

import elasticsearch as es
from fastapi import status
from fastapi.exceptions import HTTPException

from db.base import AsyncDBProxy
from models.base import BaseOrJSONModel

logger = logging.getLogger(__name__)
elastic: es.AsyncElasticsearch | None = None


async def get_elastic() -> es.AsyncElasticsearch | None:
    return elastic


class AsyncElasticProxy(AsyncDBProxy):
    def __init__(self):
        self._elastic = None

    @classmethod
    async def create(cls):
        instance = cls()
        instance._elastic = await get_elastic()
        return instance

    async def get(
        self, source: str, id_: str, model: Type[BaseOrJSONModel]
    ) -> BaseOrJSONModel | None:
        try:
            doc = await self._elastic.get(index=source, id=id_)
        except es.exceptions.ConnectionError as exc:
            logger.exception("Elastic connection error")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Search system connection error",
            ) from exc
        except es.exceptions.NotFoundError:
            return None
        return model(**doc["_source"])

    async def search(
        self, source: str, query: dict, model: Type[BaseOrJSONModel], sort: list | None = None
    ) -> list[BaseOrJSONModel] | None:
        try:
            doc_list = await self._elastic.search(index=source, body=query, sort=sort)
        except es.exceptions.ConnectionError as exc:
            logger.exception("Elastic connection error")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Search system connection error",
            ) from exc
        except es.exceptions.NotFoundError:
            return None

        list_objects = [model(**doc["_source"]) for doc in doc_list["hits"]["hits"]]
        return list_objects
