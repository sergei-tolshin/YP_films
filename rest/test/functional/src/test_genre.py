from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

WRONG_ID = "foo"
EVERY_NTH = 5

INDEX = ("genre",)


async def test_genres_count(make_get_request, test_data):
    response = await make_get_request("/genre")
    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_data["genre"])


async def test_genre_by_id(make_get_request, test_data):
    genres = test_data["genre"][::EVERY_NTH]
    for genre in genres:
        response = await make_get_request(method=f"""/genre/{genre['id']}""")

        # check main part
        assert response.body["uuid"] == genre["id"]
        assert response.body["name"] == genre["name"]


async def test_pagination(make_get_request, test_data):
    response = await make_get_request(method="/genre/", )
    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_data["genre"])
