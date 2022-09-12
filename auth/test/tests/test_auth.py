from http import HTTPStatus

import pytest
from werkzeug.http import parse_cookie

from settings import settings

BASE_URL = settings.auth_test.service_url


def test_user_refresh(login_test_user):
    response = login_test_user.client.post("{}/auth/refresh".format(BASE_URL))
    refresh_token_cookie_new = parse_cookie(response.headers.getlist("Set-Cookie")[1])["refresh_token_cookie"]
    access_token_cookie_new = parse_cookie(response.headers.getlist("Set-Cookie")[0])["access_token_cookie"]
    pytest.access_token = login_test_user.refresh_token_cookie
    pytest.refresh_token = login_test_user.access_token_cookie

    assert response.status_code == HTTPStatus.OK
    assert login_test_user.refresh_token_cookie != refresh_token_cookie_new
    assert login_test_user.access_token_cookie != access_token_cookie_new


def test_user_refresh_old_token(client):
    client.set_cookie("localhost", "access_token_cookie", pytest.access_token)
    client.set_cookie("localhost", "refresh_token_cookie", pytest.refresh_token)
    response = client.post("{}/auth/refresh".format(BASE_URL))
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_user_logout(login_test_user):
    response = login_test_user.client.post("{}/auth/logout".format(BASE_URL))
    assert response.status_code == HTTPStatus.OK
    response = login_test_user.client.post("{}/auth/logout".format(BASE_URL))
    assert response.status_code == HTTPStatus.UNAUTHORIZED
