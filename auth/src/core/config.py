import datetime
import os
from enum import Enum
# import logging
from pathlib import Path

# from core.logger import LOGGING

BASE_DIR = Path(__file__).parent.parent.absolute()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# logging.basicConfig(level=LOG_LEVEL)
# LOGGING["root"]["level"] = LOG_LEVEL


REDIS_HOST = os.getenv("AUTH_REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("AUTH_REDIS_PORT", "6380"))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

POSTGRES_HOST = os.getenv("AUTH_POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = int(os.getenv("AUTH_POSTGRES_PORT", "5433"))
POSTGRES_USER = os.getenv("AUTH_POSTGRES_USER", "postgres")
POSTGRES_DB = os.getenv("AUTH_POSTGRES_DB", "auth_database")
POSTGRES_PASSWORD = os.getenv("AUTH_POSTGRES_PASSWORD")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_COOKIE_SECURE = False
JWT_COOKIE_CSRF_PROTECT = False
JWT_TOKEN_LOCATION = ["cookies"]
JWT_SECRET_KEY = "super-secret"  # Change this in your code!
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=10)

LOCATION_SERVICE_URL = 'http://ip-api.com/json/{}'

DEFAULT_PASSWORD_TO_BASE_LENGTH = 10

JAEGER_HOST = os.getenv("JAEGER_HOST", "auth-jaeger")
JAEGER_PORT = os.getenv("JAEGER_PORT", 6831)
JAEGER_ON = True

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
URL_TO_GET_BIRTHDAY_FROM_GOOGLE = 'https://people.googleapis.com/v1/people/me?personFields=birthdays'
YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET")


class OAuthServiceNames(Enum):
    yandex = "yandex"
    google = "google"


OAUTH_YANDEX_AUTTHORIZE_URL = os.getenv("OAUTH_YANDEX_AUTTHORIZE_URL", "https://oauth.yandex.ru/authorize")
OAUTH_YANDEX_AUTTHORIZE_PARAMS = os.getenv("OAUTH_YANDEX_AUTTHORIZE_PARAMS", None)
OAUTH_YANDEX_TOKEN_URL = os.getenv("OAUTH_YANDEX_ACCESS_TOKEN_URL", "https://oauth.yandex.ru/token")
OAUTH_YANDEX_TOKEN_PARAMS = os.getenv("OAUTH_YANDEX_TOKEN_PARAMS", None)
OAUTH_YANDEX_USERINFO_ENDPOINT = os.getenv("OAUTH_YANDEX_USERINFO_ENDPOINT", "https://login.yandex.ru/info")
OAUTH_YANDEX_CLIENT_SCOPE = os.getenv("OAUTH_YANDEX_CLIENT_SCOPE", "login:info login:email login:birthday")
OAUTH_YANDEX_CLIENT_TOKEN_ENDPOINT = os.getenv("OAUTH_YANDEX_CLIENT_TOKEN_ENDPOINT", "client_secret_basic")
OAUTH_YANDEX_CLIENT_TOKEN_PLACEMENT = os.getenv("OAUTH_YANDEX_CLIENT_TOKEN_PLACEMENT", "header")
OAUTH_YANDEX_CLIENT_KWARGS = {
    "scope": OAUTH_YANDEX_CLIENT_SCOPE,
    "token_endpoint_auth_method": OAUTH_YANDEX_CLIENT_TOKEN_ENDPOINT,
    "token_placement": OAUTH_YANDEX_CLIENT_TOKEN_PLACEMENT,
}

OAUTH_GOOGLE_CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
OAUTH_GOOGLE_CLIENT_SCOPE = os.getenv(
    "OAUTH_YANDEX_NAME",
    "openid email profile https://www.googleapis.com/auth/user.birthday.read"
)
OAUTH_GOOGLE_CLIENT_KWARGS = {
    "scope": OAUTH_GOOGLE_CLIENT_SCOPE
}

SENTRY_DSN = os.getenv("SENTRY_DSN_AUTH", "")
