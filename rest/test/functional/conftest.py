import asyncio
import json
from dataclasses import dataclass

import aiofiles
import aiohttp
import pytest
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from settings import BASE_DIR, settings


@dataclass
class HTTPResponse:
    body: str
    headers: CIMultiDictProxy
    status: int


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def schema():
    async with aiofiles.open(BASE_DIR / "testdata" / "openapi.json") as oafile:
        content = await (oafile.read())
    expected_schema = json.loads(content)
    return expected_schema


@pytest.fixture(scope="session", name="es_client")
async def es_client_():
    ecfg = settings.elastic
    client = AsyncElasticsearch(
        hosts=[
            f"http://{ecfg.host}:{ecfg.port}",
        ],
    )
    yield client
    await client.close()


@pytest.fixture(scope="session", name="session")
async def session_():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(name="redis_flush", autouse=True)
async def redis_flush_():
    yield
    redis = Redis(host=settings.redis.host, port=settings.redis.port)
    await redis.flushall(asynchronous=True)
    await redis.close()


@pytest.fixture()
def make_get_request(session):
    async def inner(
            method: str,
            params: dict = None,
            root: bool = False,
    ) -> HTTPResponse:
        rcfg = settings.rest
        params = params or {}
        base_url = rcfg.root_url if root else rcfg.service_url
        url = base_url + method

        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
