from http import HTTPStatus

from argon2 import PasswordHasher
from flask import Blueprint, current_app, jsonify, request, url_for, abort
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies)
from flask_pydantic_spec import Request, Response
from user_agents import parse

from api.v1.schema import BaseResponseSchema, spec
from api.v1.schema.auth import LoginBodySchema
from api.v1.schema.cookies import CookieSchema
from api.v1.schema.user import UserRequestSchema
from api.v1.utils import (check_password_hash, get_location, get_tokens,
                          user_from_social_parse, login_history_entry_add, tracer_decorator)
from core.rate_limit import rate_limit
from models import History, PlatformEnum, User, SocialAccount
from services.db import db
from services.oauth import oauth
from services.redis import (RedisLogoutAllDevicesStorage,
                            RedisTokenRevokeStorage, redis_client)

auth = Blueprint("auth", __name__)

ERROR_AUTH = {"msg": "Incorrect username or password."}
OK_LOGIN = {"msg": "Login successful."}
OK_LOGOUT = {"msg": "Logout successful."}
REFRESH = {True: {"msg": "Refresh successful."}, False: {"msg": "Refresh failed."}}
UNAUTHORIZED = {'msg': "Unautorized"}


@auth.route("/login", methods=["POST"])
@rate_limit()
@spec.validate(
    body=Request(LoginBodySchema),
    resp=Response(
        HTTP_200=BaseResponseSchema,
        HTTP_401=BaseResponseSchema,
    ),
    tags=["auth"],
)
@tracer_decorator("login", __name__)
def login():
    username = request.json.get("login", None)
    password = request.json.get("password", None)

    # check username and password
    user = User.query.filter_by(username=username).one_or_none()

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify(ERROR_AUTH), HTTPStatus.UNAUTHORIZED

    # create tokens
    additional_claims = {
        "rol": [role.name for role in user.roles],
        "is_superuser": user.is_superuser,
    }
    access_token = create_access_token(
        identity=username, additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(identity=username)

    # add history table entry
    city = get_location(request.remote_addr)
    device = request.user_agent.string
    user_agent = parse(device)
    platform = PlatformEnum.pc
    if user_agent.is_mobile:
        platform = PlatformEnum.mobile
    elif user_agent.is_tablet:
        platform = PlatformEnum.tablet

    history_entry = History(user=user.uuid, device=device, platform=platform, location=city)
    db.session.add(history_entry)
    db.session.commit()

    # set tokens to cookies
    response = jsonify(OK_LOGIN)
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, HTTPStatus.OK


@auth.route("/logout", methods=["POST"])
@rate_limit()
@spec.validate(
    cookies=CookieSchema,
    resp=Response(
        HTTP_200=BaseResponseSchema,
        HTTP_401=BaseResponseSchema
    ),
    tags=["auth"],
)
@jwt_required(refresh=True, optional=True)
@rate_limit(rpm=50, kind="user")
def logout():
    # logout all sitch
    if isinstance(request.json, dict):
        if request.json.get("logout_all"):
            rlad = RedisLogoutAllDevicesStorage(redis_client, current_app)
            rlad.set(get_jwt_identity())

    # revoke refresh token (single logout)
    jwt = get_jwt()
    if not jwt:
        return jsonify(UNAUTHORIZED), HTTPStatus.UNAUTHORIZED

    refresh_gti = jwt.get("jti")
    rts = RedisTokenRevokeStorage(redis_client, current_app)
    rts.add_token(refresh_gti)
    response = jsonify(OK_LOGOUT)
    unset_jwt_cookies(response)
    return response, HTTPStatus.OK


@auth.route("/refresh", methods=["POST"])
@rate_limit()
@spec.validate(
    cookies=CookieSchema,
    resp=Response(
        HTTP_200=BaseResponseSchema,
    ),
    tags=["auth"],
)
@jwt_required(refresh=True)
@rate_limit(rpm=50, kind="user")
def refresh():
    identity = get_jwt_identity()
    jwt = get_jwt()
    refresh_gti = jwt.get("jti")

    # check if logged out from all devices
    rlad = RedisLogoutAllDevicesStorage(redis_client, current_app)
    check_logout_all = rlad.check_logout_all(jwt)
    if check_logout_all:
        response = jsonify(REFRESH[check_logout_all])
        return response, HTTPStatus.UNAUTHORIZED

    # check in rev. storage (single logout)
    rts = RedisTokenRevokeStorage(redis_client, current_app)
    check = rts.check_token(refresh_gti)
    response = jsonify(REFRESH[check])
    if check:
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, HTTPStatus.OK
    else:
        return response, HTTPStatus.UNAUTHORIZED


@auth.route('/login/<name>')
def login_oauth(name):
    client = oauth.create_client(name)
    if not client:
        abort(404)
    redirect_uri = url_for('auth.auth_name', name=name, _external=True)
    return client.authorize_redirect(redirect_uri)


@auth.route('/auth/<name>')
def auth_name(name):
    client = oauth.create_client(name)
    if not client:
        abort(404)
    token = client.authorize_access_token()
    sub, user_info_from_social = user_from_social_parse(name, token, client)

    # # Check in base user by social id
    check_user_registration = SocialAccount.query.filter_by(social_id=sub, social_name=name).one_or_none()

    if check_user_registration:
        user_from_db = User.query.get(check_user_registration.access_token)
    else:
        # Validate data by pydantic model
        user_to_create = UserRequestSchema(**user_info_from_social)
        data_for_user_model = user_to_create.dict()

        # Set password
        ph = PasswordHasher()
        data_for_user_model.update({"password_hash": ph.hash(data_for_user_model.pop("password"))})

        # Create entry in database
        user_to_save = User(**data_for_user_model)
        social_account = SocialAccount(social_id=sub, social_name=name)
        user_to_save.social_accounts.append(social_account)
        db.session.add(user_to_save)
        db.session.commit()

        user_from_db = User.query.filter_by(username=data_for_user_model["username"]).one_or_none()

    access_token, refresh_token = get_tokens(user_from_db)
    login_history_entry_add(user_from_db)
    response = jsonify(OK_LOGIN)
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, HTTPStatus.OK
