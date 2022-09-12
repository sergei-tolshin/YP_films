import abc
from typing import Type
from models.base import BaseOrJSONModel


class AsyncCacheProxy(abc.ABC):
    @abc.abstractmethod
    async def put(self, key: str, data: object):
        pass

    @abc.abstractmethod
    async def get(
        self, key: str, model: Type[BaseOrJSONModel]
    ) -> BaseOrJSONModel | list[BaseOrJSONModel] | None:
        pass


class AsyncDBProxy(abc.ABC):
    @abc.abstractmethod
    async def get(
        self, source: str, id_: str, model: Type[BaseOrJSONModel]
    ) -> BaseOrJSONModel | None:
        pass

    @abc.abstractmethod
    async def search(
        self, source: str, query: dict, model: Type[BaseOrJSONModel], sort: list | None = None
    ) -> list[BaseOrJSONModel] | None:
        pass
