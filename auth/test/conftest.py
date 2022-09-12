import json
import sys

import psycopg2
import pytest
from argon2 import PasswordHasher
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.http import parse_cookie

from settings import settings, BASE_DIR

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{settings.postgres_test.user}:{settings.postgres_test.password}@"
    f"{settings.postgres_test.host}:{settings.postgres_test.port}/{settings.postgres_test.database}"
)
sys.path.insert(1, "../auth/src/")
TEST_DATA_USERS = json.loads(
    open(BASE_DIR / "testdata" / "users_create_user.json", "r").read()
)
BASE_URL = settings.auth_test.service_url


class LoggedUser:
    def __init__(self, client, user, access_token_cookie, refresh_token_cookie):
        """
        Logged User.

        :param client: Client with access_token in cookies.
        :param user: User logged data.
        :param access_token_cookie: User access token.
        :param refresh_token_cookie: User refresh token.
        """
        self.client = client
        self.user = user
        self.access_token_cookie = access_token_cookie
        self.refresh_token_cookie = refresh_token_cookie


def pytest_configure():
    pytest.shared = ""
    pytest.access_token = ""
    pytest.refresh_token = ""


@pytest.fixture(scope="session", name="create_testdb")
def create_testdb_():
    """Create database for tests."""
    con = psycopg2.connect(
        user=settings.postgres_test.user,
        password=settings.postgres_test.password,
        host=settings.postgres_test.host,
        port=settings.postgres_test.port,
        dbname="postgres",
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    name_database = settings.postgres_test.database
    try:
        with con.cursor() as cursor:
            sql_create_database = "create database " + name_database + ";"
            cursor.execute(sql_create_database)
    except psycopg2.ProgrammingError:
        pass
    yield


@pytest.fixture(scope="session")
def app(create_testdb):
    """Create Flask app for tests."""
    from app import create_app
    from services.db import db

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI,
            "JWT_TOKEN_LOCATION": ["cookies"]
        },
    )
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="session", name="client")
def client_(app):
    """Create client for tests requests."""
    return app.test_client(use_cookies=True)


@pytest.fixture(scope="package", name="create_test_user")
def create_test_user_(app):
    """Create test User in Postgres."""
    from models.user import User
    from services.db import db

    user = TEST_DATA_USERS[1]
    ph = PasswordHasher()
    not_hash_pass = user.pop("password")
    user.update({"password_hash": ph.hash(not_hash_pass)})
    with app.app_context():
        db.session.add(User(**user))
        db.session.commit()
    user.update({"password": not_hash_pass})
    yield user


@pytest.fixture()
def login_test_user(client, create_test_user):
    """Login test User."""
    """
    authorization_string_bytes = base64.b64encode(
        bytes(
            "{}:{}".format(create_test_user["username"], create_test_user["password"]),
            "utf-8",
        )
    )
    authorization_string = "Basic {}".format(authorization_string_bytes.decode("utf-8"))
    """
    response = client.post(
        "{}/auth/login".format(BASE_URL),
        json={'login': create_test_user['username'], 'password': create_test_user['password']}
    )

    access_token_cookie = parse_cookie(response.headers.getlist("Set-Cookie")[0])[
        "access_token_cookie"
    ]
    refresh_token_cookie = parse_cookie(response.headers.getlist("Set-Cookie")[1])[
        "refresh_token_cookie"
    ]
    yield LoggedUser(
        client=client,
        user=create_test_user,
        access_token_cookie=access_token_cookie,
        refresh_token_cookie=refresh_token_cookie,
    )
    client.delete_cookie("localhost", "access_token_cookie")
    client.delete_cookie("localhost", "refresh_token_cookie")
