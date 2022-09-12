import json
from collections import defaultdict

import aiofiles
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from settings import BASE_DIR

CHUNK_INDEX = 0


@pytest.fixture(scope="module", name="index")
async def index_(es_client: AsyncElasticsearch, request):
    el_indexes = getattr(request.module, "INDEX")
    for index_name in el_indexes:
        path = BASE_DIR / "testdata" / "index" / f"{index_name}.json"
        if not await es_client.indices.exists(index=[index_name]):
            async with (aiofiles.open(path, encoding="utf-8")) as index_file:
                index_data = await index_file.read()
                index_data = json.loads(index_data)
            await es_client.indices.create(
                index=index_name,
                settings=index_data["settings"],
                mappings=index_data["mappings"],
            )
    yield None
    await es_client.indices.delete(index=el_indexes)


@pytest.fixture(scope="module")
async def test_data(es_client: AsyncElasticsearch, index, request):
    el_indexes = getattr(request.module, "INDEX")
    data: dict[str, list] = {}
    for index_name in el_indexes:
        path = BASE_DIR / "testdata" / f"{index_name}_{CHUNK_INDEX}.json"
        async with (aiofiles.open(path, encoding="utf-8")) as data_file:
            index_data = await data_file.read()
            index_data = json.loads(index_data)
            data[index_name] = index_data
            await async_bulk(es_client, index_data, refresh="wait_for")
    yield data


@pytest.fixture(scope="module")
async def films_by_persons(test_data):
    result = defaultdict(list)
    for film in test_data["movies"]:
        for person_role in ["actors", "writers", "directors"]:
            for person in film[person_role]:
                person_id = person["id"]
                result[person_id].append(film["id"])
    return result
