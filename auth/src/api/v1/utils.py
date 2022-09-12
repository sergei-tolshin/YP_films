import datetime
import json
import random
import string
from functools import wraps
from uuid import UUID

import requests
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from authlib.integrations.requests_client import OAuth2Session
from flask import current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token
from opentelemetry import trace
from werkzeug.exceptions import NotFound

from core.config import JAEGER_ON
from models import User, History
from services.db import db
from services.oauth import oauth


def tracer_decorator(name: str, tracer_name: str):
    tracer = trace.get_tracer(tracer_name)

    def wrapper(func):
        if not JAEGER_ON:
            return func

        @wraps(func)
        def inner(*args, **kwargs):
            with tracer.start_as_current_span(name):
                return func(*args, **kwargs)

        return inner

    return wrapper


def get_random_string(length: int, lowercase: bool = False, digits: bool = True) -> str:
    letters = string.ascii_lowercase if lowercase else string.ascii_letters
    digits = string.digits if digits else ""
    box = letters + digits
    return "".join(random.choice(box) for _ in range(length))


def check_uuid(uuid_str: str):
    try:
        UUID(uuid_str)
    except ValueError as err:
        raise NotFound from err


def check_password_hash(stored_hash: str, password: str) -> bool:
    try:
        ph = PasswordHasher()
        ph.verify(stored_hash, password)
        return True
    except VerifyMismatchError:
        return False


@tracer_decorator("get_location", __name__)
def get_location(ip_address: str) -> str | None:
    try:
        location_request = requests.get(current_app.config['LOCATION_SERVICE_URL'].format(ip_address))
        city = json.loads(location_request.text)['city']
    except (KeyError, requests.exceptions.ConnectionError):
        return None
    return city


def get_username_from_email(email: str) -> str:
    """Create username from email, if username exist in database, create username + random string."""
    username_from_email = email.split("@")[0]
    username = username_from_email
    while True:
        user_from_db = User.query.filter_by(username=username).one_or_none()
        if not user_from_db:
            break
        username = username + get_random_string(4, lowercase=True)
    return username


def get_tokens(user: User) -> tuple:
    """Create access and refresh tokens."""
    additional_claims = {
        "rol": [role.name for role in user.roles],
        "is_superuser": user.is_superuser,
    }
    access_token = create_access_token(
        identity=user.username, additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(identity=user.username)
    return access_token, refresh_token


def get_birthday_google(token: dict) -> datetime.date:
    """Get birthday in Google account."""
    client = OAuth2Session(
        current_app.config["GOOGLE_CLIENT_ID"],
        current_app.config["GOOGLE_CLIENT_SECRET"],
        token=token
    )
    resp = client.get(current_app.config["URL_TO_GET_BIRTHDAY_FROM_GOOGLE"])
    birthday_data = resp.json()["birthdays"][0]["date"]
    birthday = datetime.date(**birthday_data)
    return birthday


def user_from_social_parse(name: str, token: dict, client: oauth) -> tuple:
    """Parser from social service data."""
    user_info = token.get("userinfo")
    if not user_info:
        user_info = client.userinfo(token=token)
    match name:
        case "google":
            sub = user_info["sub"]
            birthday = get_birthday_google(token)
            user = {
                "username": get_username_from_email(user_info["email"]),
                "first_name": user_info["given_name"],
                "last_name": user_info["family_name"],
                "birth_date": birthday,
                "email": user_info["email"],
                "password": get_random_string(current_app.config["DEFAULT_PASSWORD_TO_BASE_LENGTH"])
            }
            return sub, user
        case "yandex":
            sub = user_info["id"]
            birthday = datetime.datetime.strptime(user_info["birthday"], "%Y-%m-%d").date()
            user = {
                "username": get_username_from_email(user_info["emails"][0]),
                "first_name": user_info["first_name"],
                "last_name": user_info["last_name"],
                "birth_date": birthday,
                "email": user_info["emails"][0],
                "password": get_random_string(current_app.config["DEFAULT_PASSWORD_TO_BASE_LENGTH"])
            }
            return sub, user


def login_history_entry_add(user: User):
    """User history login table entry add."""
    city = get_location(request.remote_addr)
    device = request.headers.get("User-Agent")
    history_entry = History(user=user.uuid, device=device, location=city)
    db.session.add(history_entry)
    db.session.commit()
