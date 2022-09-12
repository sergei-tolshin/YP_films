from http import HTTPStatus

import pytest

WRONG_ID = "foo"
EVERY_NTH = 5
INDEX = ("movies", "person")

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_person_by_id(make_get_request, test_data):
    # First, successful attempts
    persons = test_data["person"][::EVERY_NTH]
    for person in persons:
        response = await make_get_request(method=f"""/person/{person['id']}""")

        # check main part
        assert response.body["uuid"] == person["id"]
        assert response.body["full_name"] == person["full_name"]
        assert response.body["role"] == ",".join(
            [item["role"] for item in person["roles"]]
        )

        # check person film ids
        for role in person["roles"]:
            assert all(
                [fw_id in response.body["film_ids"] for fw_id in role["film_work_ids"]]
            )

    # Second,
    response = await make_get_request(method=f"""/person/{WRONG_ID}""")
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "person_id",
    [
        "a3468637-c3c3-442c-892e-1625385c49c6",  # actor
        "6406101c-18ea-4d8a-9c7d-6c0a506a2b78",  # writer
        "2ede5838-9b45-4ba0-a369-dc7acce459bc",  # actor writer director
    ],
)
async def test_person_id_film(make_get_request, test_data, films_by_persons, person_id):
    film_ids = films_by_persons[person_id]

    # check that all film ids are given by the endpoint
    response = await make_get_request(method=f"""/person/{person_id}/film""")
    response_film_ids = [film["uuid"] for film in response.body]

    for film_id in film_ids:
        assert film_id in response_film_ids


async def test_wrong_person_id_film(make_get_request, test_data):
    response = await make_get_request(method=f"""/person/{WRONG_ID}/film""")
    assert response.status == HTTPStatus.NOT_FOUND
