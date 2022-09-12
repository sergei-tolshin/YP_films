from http import HTTPStatus

import pytest

from .search_queries import *

INDEX = ("movies", "person")

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("query", FILM_QUERY_DEFAULT_PARAM)
async def test_film_search_with_default_params(make_get_request, test_data, query):
    response = await make_get_request(
        method="/film/search", params={"query": query["query"]}
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == query["count"]
    assert response.body[0]["uuid"] == query["first"][0]
    assert response.body[0]["title"] == query["first"][1]
    assert response.body[0]["imdb_rating"] == query["first"][2]
    assert response.body[-1]["uuid"] == query["last"][0]
    assert response.body[-1]["title"] == query["last"][1]
    assert response.body[-1]["imdb_rating"] == query["last"][2]


@pytest.mark.parametrize("query", FILM_QUERY)
async def test_film_search_first(make_get_request, test_data, query):
    response = await make_get_request(
        method="/film/search",
        params={
            "query": query["query"],
            "sort": "-relevance",
            "page[size]": 3,
            "page[number]": 1,
        },
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 3
    assert response.body[0]["uuid"] == query["first"][0]
    assert response.body[0]["title"] == query["first"][1]
    assert response.body[0]["imdb_rating"] == query["first"][2]


@pytest.mark.parametrize("query", FILM_QUERY)
async def test_film_search_last(make_get_request, test_data, query):
    response = await make_get_request(
        method="/film/search",
        params={
            "query": query["query"],
            "sort": "-relevance",
            "page[size]": query["count"] - 1,
            "page[number]": 2,
        },
    )

    assert len(response.body) == 1
    assert response.body[0]["uuid"] == query["last"][0]
    assert response.body[0]["title"] == query["last"][1]
    assert response.body[0]["imdb_rating"] == query["last"][2]


@pytest.mark.parametrize("query", PERSON_QUERY_DEFAULT_PARAM)
async def test_person_search_with_default_params(make_get_request, test_data, query):
    response = await make_get_request(
        method="/person/search", params={"query": query["query"]}
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == query["count"]
    assert response.body[0]["uuid"] == query["first"][0]
    assert response.body[0]["full_name"] == query["first"][1]
    assert response.body[0]["role"] == query["first"][2]
    assert response.body[0]["film_ids"][0] == query["first"][3][0]
    assert response.body[0]["film_ids"][-1] == query["first"][3][-1]
    assert response.body[-1]["uuid"] == query["last"][0]
    assert response.body[-1]["full_name"] == query["last"][1]
    assert response.body[-1]["role"] == query["last"][2]
    assert response.body[-1]["film_ids"][0] == query["last"][3][0]
    assert response.body[-1]["film_ids"][-1] == query["last"][3][-1]


@pytest.mark.parametrize("query", PERSON_QUERY)
async def test_person_search_first(make_get_request, test_data, query):
    response = await make_get_request(
        method="/person/search",
        params={
            "query": query["query"],
            "sort": "-relevance",
            "page[size]": 2,
            "page[number]": 1,
        },
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2
    assert response.body[0]["uuid"] == query["first"][0]
    assert response.body[0]["full_name"] == query["first"][1]
    assert response.body[0]["role"] == query["first"][2]
    assert response.body[0]["film_ids"][0] == query["first"][3][0]
    assert response.body[0]["film_ids"][-1] == query["first"][3][-1]


@pytest.mark.parametrize("query", PERSON_QUERY)
async def test_person_search_last(make_get_request, test_data, query):
    response = await make_get_request(
        method="/person/search",
        params={
            "query": query["query"],
            "sort": "-relevance",
            "page[size]": query["count"] - 1,
            "page[number]": 2,
        },
    )

    assert len(response.body) == 1
    assert response.body[0]["uuid"] == query["last"][0]
    assert response.body[0]["full_name"] == query["last"][1]
    assert response.body[0]["role"] == query["last"][2]
    assert response.body[0]["film_ids"][0] == query["last"][3][0]
    assert response.body[0]["film_ids"][-1] == query["last"][3][-1]


async def test_film_bad_query_search(make_get_request, test_data):
    response = await make_get_request(method="/film/search", params={"query": "1jfwiodjioweio"})
    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body["detail"] != ""


async def test_person_bad_query_search(make_get_request, test_data):
    response = await make_get_request(method="/person/search", params={"query": "1jf12312djioweio"})
    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body["detail"] != ""


@pytest.mark.parametrize("sort_param", ["test", 1234, "-name", "rating"])
async def test_bad_sort_param_search_film(make_get_request, test_data, sort_param):
    response = await make_get_request(method="/film/search", params={"sort": sort_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


@pytest.mark.parametrize("sort_param", ["test", 1234, "-name", "rating"])
async def test_bad_sort_param_search_person(make_get_request, test_data, sort_param):
    response = await make_get_request(method="/person/search", params={"sort": sort_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


@pytest.mark.parametrize("page_param", ["bad", "test", "-name", "uuid", -1])
async def test_bad_page_param_search_film_page_size(make_get_request, test_data, page_param):
    response = await make_get_request(method="/film/search", params={"page[size]": page_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


@pytest.mark.parametrize("page_param", ["bad", "test", "-name", "uuid", -1])
async def test_bad_page_param_search_film_page_number(make_get_request, test_data, page_param):
    response = await make_get_request(method="/film/search", params={"page[number]": page_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


@pytest.mark.parametrize("page_param", ["bad", "test", "-name", "uuid", -1])
async def test_bad_page_param_search_person_page_size(make_get_request, test_data, page_param):
    response = await make_get_request(method="/person/search", params={"page[size]": page_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


@pytest.mark.parametrize("page_param", ["bad", "test", "-name", "uuid", -1])
async def test_bad_page_param_search_person_page_number(make_get_request, test_data, page_param):
    response = await make_get_request(method="/person/search", params={"page[number]": page_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""
