import json
from http import HTTPStatus

import pytest

from settings import BASE_DIR, settings

BASE_URL = settings.auth_test.service_url
TEST_DATA = json.loads(open(BASE_DIR / "testdata" / "users_create_user.json", "r").read())
PATCH_DATA = {
    "first_name": "NEW_First1",
    "last_name": "NEW_Last1"
}


def test_user_create(client):
    user = TEST_DATA[0]
    response = client.post("{}/users/".format(BASE_URL), json=user)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json["username"] == user["username"]
    assert response.json["first_name"] == user["first_name"]
    assert response.json["last_name"] == user["last_name"]
    assert response.json["email"] == user["email"]
    assert response.json["birth_date"] == user["birth_date"]


def test_get_self_info(login_test_user):
    response = login_test_user.client.get("{}/users/get-me".format(BASE_URL))

    assert response.status_code == HTTPStatus.OK
    assert response.json["username"] == login_test_user.user["username"]
    assert response.json["first_name"] == login_test_user.user["first_name"]
    assert response.json["last_name"] == login_test_user.user["last_name"]
    assert response.json["email"] == login_test_user.user["email"]
    assert response.json["birth_date"] == login_test_user.user["birth_date"]


def test_get_self_info_guest(client):
    response = client.get("{}/users/get-me".format(BASE_URL))
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_patch_user(login_test_user):
    response = login_test_user.client.patch("{}/users/".format(BASE_URL), json=PATCH_DATA)
    assert response.status_code == HTTPStatus.OK
    response = login_test_user.client.get("{}/users/get-me".format(BASE_URL))

    assert response.json["username"] == login_test_user.user["username"]
    assert response.json["first_name"] == PATCH_DATA["first_name"]
    assert response.json["last_name"] == PATCH_DATA["last_name"]
    assert response.json["email"] == login_test_user.user["email"]
    assert response.json["birth_date"] == login_test_user.user["birth_date"]


def test_get_user_history(login_test_user):
    response = login_test_user.client.get("{}/users/get-me".format(BASE_URL))
    uuid = response.json["uuid"]
    pytest.shared = uuid
    response = login_test_user.client.get("{}/users/{}/history".format(BASE_URL, uuid))

    assert response.status_code == HTTPStatus.OK
    assert response.json != list()


def test_get_user_history_guest(client):
    response = client.get("{}/users/{}/history".format(BASE_URL, pytest.shared))
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_user_delete(login_test_user):
    response = login_test_user.client.delete("{}/users/".format(BASE_URL))
    assert response.status_code == HTTPStatus.NO_CONTENT
