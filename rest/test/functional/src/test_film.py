from http import HTTPStatus

import pytest

INDEX = ("genre", "movies", "person")

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_films_count(make_get_request, test_data):
    response = await make_get_request("/film")

    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_data["movies"])


async def test_default_params(make_get_request, test_data):
    loaded_data = sorted(test_data["movies"], key=lambda d: d['imdb_rating'], reverse=True)

    response = await make_get_request("/film")

    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_data["movies"])
    assert response.body[0]["imdb_rating"] == loaded_data[0]["imdb_rating"]
    assert response.body[24]["imdb_rating"] == loaded_data[24]["imdb_rating"]
    assert response.body[57]["imdb_rating"] == loaded_data[57]["imdb_rating"]
    assert response.body[-1]["imdb_rating"] == loaded_data[-1]["imdb_rating"]


async def test_params(make_get_request, test_data):
    response = await make_get_request(
        method="/film/",
        params={"page[size]": 35, "page[number]": 1, "sort": "imdb_rating"},
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 35
    assert response.body[0]["imdb_rating"] == 2.1
    assert response.body[-1]["imdb_rating"] == 6.7


async def test_filter_genre(make_get_request, test_data):
    genre = test_data["genre"][2]["id"]

    response = await make_get_request(
        method="/film/",
        params={
            "page[size]": 150,
            "page[number]": 1,
            "sort": "imdb_rating",
            "filter_genre": genre,
        },
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 25
    assert response.body[0]["imdb_rating"] == 3.9
    assert response.body[-1]["imdb_rating"] == 9.6


async def test_bad_filter_genre(make_get_request, test_data):
    response = await make_get_request(
        method="/film/",
        params={
            "page[size]": 150,
            "page[number]": 1,
            "sort": "imdb_rating",
            "filter_genre": "dfhweyueh123",
        },
    )

    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body["detail"] != ""


@pytest.mark.parametrize("page_size,page_number,count", [(40, 1, 40), (40, 2, 40), (40, 3, 20), ])
async def test_pagination(make_get_request, test_data, page_size, page_number, count):
    response = await make_get_request(method="/film/", params={"page[size]": page_size, "page[number]": page_number}, )
    assert response.status == HTTPStatus.OK
    assert len(response.body) == count


async def test_out_of_pagination(make_get_request, test_data):
    response = await make_get_request(method="/film/", params={"page[size]": 40, "page[number]": 4})
    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body["detail"] != ""


async def test_by_id(make_get_request, test_data):
    data_movies = test_data["movies"]

    film = data_movies[14]
    genres, actors, writers, directors = film["genres"], film["actors"], film["writers"], film["directors"]

    response = await make_get_request(method="/film/{}".format(film["id"]))

    assert response.status == HTTPStatus.OK
    assert response.body["uuid"] == film["id"]
    assert response.body["title"] == film["title"]
    assert response.body["description"] == film["description"]
    if genres:
        assert len(response.body["genres"]) == len(genres)
        assert len(response.body["genres"][0]["uuid"]) == len(genres[0]["id"])
        assert len(response.body["genres"][0]["name"]) == len(genres[0]["name"])
    if actors:
        assert len(response.body["actors"]) == len(actors)
        assert len(response.body["actors"][0]["uuid"]) == len(actors[0]["id"])
        assert len(response.body["actors"][0]["full_name"]) == len(actors[0]["name"])
    if writers:
        assert len(response.body["writers"]) == len(writers)
        assert len(response.body["writers"][0]["uuid"]) == len(writers[0]["id"])
        assert len(response.body["writers"][0]["full_name"]) == len(writers[0]["name"])
    if directors:
        assert len(response.body["directors"]) == len(directors)
        assert len(response.body["directors"][0]["uuid"]) == len(directors[0]["id"])
        assert len(response.body["directors"][0]["full_name"]) == len(directors[0]["name"])


@pytest.mark.parametrize("film_id", ["quwehdfqwuih", 15253, 0])
async def test_bad_id(make_get_request, test_data, film_id):
    response = await make_get_request(method="/film/{}".format(film_id))
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


@pytest.mark.parametrize("film_id", ["b501ced6-fff1-493a-ad41-73449b55ffee"])
async def test_not_found_id(make_get_request, test_data, film_id):
    response = await make_get_request(method="/film/{}".format(film_id))
    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body["detail"] != ""


@pytest.mark.parametrize("person_index,films_count", [(0, 1), (5, 10), (-1, 1), (50, 3)])
async def test_films_by_person(make_get_request, test_data, person_index, films_count):
    film_ids = sum([role["film_work_ids"] for role in test_data["person"][person_index]["roles"]], [])

    response = await make_get_request(method="/person/{}/film".format(test_data["person"][person_index]["id"]))

    assert response.status == HTTPStatus.OK
    assert len(response.body) == films_count
    for film in response.body:
        assert film["uuid"] in film_ids


@pytest.mark.parametrize("film_id", ["quwehdfqwuih", 15253, 0])
async def test_films_by_bad_person(make_get_request, test_data, film_id):
    response = await make_get_request(method="/person/{}/film".format(film_id))
    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body["detail"] != ""


@pytest.mark.parametrize("sort_param", ["test", 1234, "-name", "rating", ""])
async def test_bad_sort_param(make_get_request, test_data, sort_param):
    response = await make_get_request(method="/film/", params={"sort": sort_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


@pytest.mark.parametrize("page_param", ["bad", "test", "-name", "uuid", -1])
async def test_bad_page_param_size(make_get_request, test_data, page_param):
    response = await make_get_request(method="/film/", params={"page[size]": page_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


@pytest.mark.parametrize("page_param", ["bad", "test", "-name", "uuid", -1])
async def test_bad_page_param_number(make_get_request, test_data, page_param):
    response = await make_get_request(method="/film/", params={"page[number]": page_param})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


async def test_out_of_page_size(make_get_request, test_data):
    response = await make_get_request(method="/film/", params={"page[size]": 500000})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.body["detail"] != ""


async def test_out_of_page_number(make_get_request, test_data):
    response = await make_get_request(method="/film/", params={"page[number]": 1001})
    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body["detail"] != ""


async def test_bad_param(make_get_request, test_data):
    response = await make_get_request(method="/film/", params={"test_1": 10, "test_2": 1})
    assert response.status == HTTPStatus.OK
    assert len(response.body) == len(test_data["movies"])
