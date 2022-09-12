import getpass
import json
from http import HTTPStatus

from argon2 import PasswordHasher
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import (get_jwt_identity, jwt_required,
                                unset_jwt_cookies)
from flask_pydantic_spec import Response as SpecResponse
from opentelemetry import trace
from sqlalchemy.exc import IntegrityError

from api.v1.schema import BaseResponseSchema, spec
from api.v1.schema.cookies import CookieSchema
from api.v1.schema.role import RoleListResponseSchema
from api.v1.schema.user import (HistoryListResponse, HistoryResponse,
                                UserRequestSchema, UserResponseSchema,
                                UserUpdateRequestSchema, Pagination)
from api.v1.utils import check_uuid
from core.permissions import user_or_admin
from core.rate_limit import rate_limit
from models.role import Role
from models.user import User
from services.db import db
from services.redis import RedisLogoutAllDevicesStorage, redis_client

users = Blueprint("users", __name__)
from flask import current_app

USER_DELETE_OK = {"msg": "User delete successful."}
USER_NOT_FOUND = {"msg": "User not found."}
USER_ALREADY_EXIST = {"msg": "User already exists."}
ROLE_ADD_OK = {"msg": "Role added sucsesfully"}
ROLE_NOT_FOUND = {"msg": "Role not found."}
ROLE_REMOVE_OK = {"msg": "Role removed sucsesfully"}
USER_ALREADY_HAS_ROLE = {"msg": "User already exist this role"}

tracer = trace.get_tracer(__name__)


@users.cli.command('create-superuser')
def create_admin():
    ph = PasswordHasher()
    username = input("login: ")
    email = input("email: ")
    password, password_again = "dump", ""
    while password != password_again:
        password = getpass.getpass(prompt="password: ")
        password_again = getpass.getpass(prompt="again: ")
    superuser = User(username=username, email=email, password_hash=ph.hash(password), superuser=True)

    db.session.add(superuser)
    db.session.commit()


@users.route("/get-me", methods=["GET"])
@rate_limit()
@spec.validate(
    cookies=CookieSchema,
    resp=SpecResponse(
        HTTP_200=UserResponseSchema,
    ),
    tags=["users"],
)
@jwt_required()
@rate_limit(rpm=50, kind="user")
def get_me():
    """
    Method to get self user info.
    """
    identity = get_jwt_identity()
    db_user = User.query.filter_by(username=identity).one_or_none()
    if db_user:
        user = UserResponseSchema.from_orm(db_user)
        return jsonify(user.dict())
    return Response(
        json.dumps(USER_NOT_FOUND),
        mimetype="application/json",
        status=HTTPStatus.NOT_FOUND,
    )


@users.route("/", methods=["POST"])
@rate_limit()
@spec.validate(
    body=UserRequestSchema,
    resp=SpecResponse(HTTP_201=UserResponseSchema, HTTP_400=BaseResponseSchema),
    tags=["users"],
)
@rate_limit(rpm=50, kind="user")
def create_user():
    """
    Method to create user in database.
    """
    current_app.logger.info("User create start.")
    request_id = request.headers.get('X-Request-Id')
    with tracer.start_as_current_span("Create user"):
        span = trace.get_current_span()
        span.set_attribute("Request-Id", request_id)
        data = request.get_json()
        ph = PasswordHasher()
        data.update({"password_hash": ph.hash(data.pop("password"))})
        with tracer.start_as_current_span("create_db"):
            span = trace.get_current_span()
            span.set_attribute("Request-Id", request_id)
            db.session.add(User(**data))
            try:
                db.session.commit()
                current_app.logger.info("User create successful.")
            except IntegrityError as err:
                current_app.logger.warning("User create fail - {}".format(err._message()))
                msg = err._message().split("DETAIL:  ")[1].strip()
                return jsonify({"msg": msg}), HTTPStatus.BAD_REQUEST
            user_from_db = User.query.filter_by(username=data["username"]).one_or_none()
            response = UserResponseSchema.from_orm(user_from_db)

    return jsonify(response.dict()), HTTPStatus.CREATED


@users.route("/", methods=["PATCH"])
@rate_limit()
@spec.validate(
    body=UserUpdateRequestSchema,
    resp=SpecResponse(HTTP_200=UserResponseSchema, HTTP_400=BaseResponseSchema),
    tags=["users"],
)
@jwt_required()
@rate_limit(rpm=50, kind="user")
def patch_user():
    """
    Method to edit user in database.
    """
    identity = get_jwt_identity()
    user_from_db = User.query.filter_by(username=identity).first()
    user_uuid = user_from_db.uuid
    user = UserResponseSchema.from_orm(user_from_db)
    data = request.get_json()

    # check password change
    try:
        new_password = data.pop("password")
    except KeyError:
        pass
    else:
        ph = PasswordHasher()
        user_from_db.password_hash = ph.hash(new_password)

    # check other fields
    fields_to_update = [value for value in data.keys() if value in user.__fields__]
    for field in fields_to_update:
        setattr(user, field, data[field])
    for field in fields_to_update:
        value_to_update = getattr(user, field)
        setattr(user_from_db, field, value_to_update)
    try:
        db.session.commit()
    except IntegrityError as err:
        msg = err._message().split("DETAIL:  ")[1].strip()
        return jsonify({"msg": msg}), HTTPStatus.BAD_REQUEST
    response = UserResponseSchema.from_orm(User.query.get(user_uuid))
    return jsonify(response.dict())


@users.route("/", methods=["DELETE"])
@rate_limit()
@spec.validate(
    resp=SpecResponse(HTTP_200=UserResponseSchema, HTTP_400=BaseResponseSchema),
    tags=["users"],
)
@jwt_required()
@rate_limit(rpm=50, kind="user")
def delete_user():
    """
    Method to delete self user in database.
    """
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        rlad = RedisLogoutAllDevicesStorage(redis_client, current_app)
        rlad.set(identity)
        response = jsonify(USER_DELETE_OK)
        unset_jwt_cookies(response)
        return response, HTTPStatus.NO_CONTENT
    return Response(
        json.dumps(USER_NOT_FOUND),
        mimetype="application/json",
        status=HTTPStatus.BAD_REQUEST,
    )


@users.route("/roles", methods=["GET"])
@rate_limit()
@spec.validate(
    resp=SpecResponse(
        HTTP_200=RoleListResponseSchema,
        HTTP_403=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["user-role"],
)
def users_get_my_roles_by_id():
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
        return USER_NOT_FOUND, HTTPStatus.NOT_FOUND
    roles_list = user.roles
    permission_level = max(role.permission_level for role in roles_list)
    roles = RoleListResponseSchema(roles=roles_list, permission_level=permission_level)
    return jsonify(roles.dict())


@users.route("/<user_id>", methods=["GET"])
@rate_limit()
@spec.validate(
    resp=SpecResponse(HTTP_200=UserResponseSchema, HTTP_404=BaseResponseSchema),
    tags=["users"],
)
# @jwt_required()
@rate_limit(rpm=50, kind="user")
def get_user_by_id(user_id):
    """
    Method to get user info by id.
    """
    user_from_db = User.query.get_or_404(user_id)
    user = UserResponseSchema.from_orm(user_from_db).dict()
    return jsonify(user), HTTPStatus.OK


@users.route("/<user_id>/history", methods=["GET"])
@rate_limit()
@jwt_required()
@spec.validate(
    resp=SpecResponse(
        HTTP_200=HistoryListResponse,
        HTTP_403=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["history"],
    query=Pagination
)
@rate_limit(rpm=50, kind="user")
@user_or_admin()
def users_get_history_by_id(user_id):
    """
    Method to get user login history info by id.
    """
    check_uuid(user_id)
    pagination = Pagination(page=request.args.get("page", None), page_size=request.args.get("page_size", None))
    user_from_db = User.query.get_or_404(user_id)
    histories = [
        HistoryResponse.from_orm(hist) for hist in
        user_from_db.history.paginate(
            page=pagination.page,
            per_page=pagination.page_size,
            error_out=False,
            max_per_page=10
        ).items
    ]

    resp = HistoryListResponse(history_list=histories)

    return jsonify(resp.dict()), HTTPStatus.OK


@users.route("/<user_id>/roles", methods=["GET"])
@rate_limit()
@spec.validate(
    resp=SpecResponse(
        HTTP_200=RoleListResponseSchema,
        HTTP_403=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["user-role"],
)
def users_get_roles_by_id(user_id):
    check_uuid(user_id)

    user = User.query.get_or_404(user_id)
    roles_list = user.roles
    permission_level = max(role.permission_level for role in roles_list)
    roles = RoleListResponseSchema(roles=roles_list, permission_level=permission_level)
    return jsonify(roles.dict())


@users.route("/<user_id>/roles/<role_id>", methods=["PUT"])
@rate_limit()
@spec.validate(
    resp=SpecResponse(
        HTTP_200=BaseResponseSchema,
        HTTP_403=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["user-role"],
)
def users_add_role_by_id(user_id, role_id):
    check_uuid(user_id)
    check_uuid(role_id)

    user_from_db = User.query.get_or_404(user_id)
    role_from_db = Role.query.get_or_404(role_id)
    if role_from_db not in user_from_db.roles:
        user_from_db.roles.append(role_from_db)
        try:
            db.session.commit()
        except IntegrityError as err:
            msg = err._message().split("DETAIL:  ")[1].strip()
            return jsonify({"msg": msg}), HTTPStatus.BAD_REQUEST
        return jsonify(ROLE_ADD_OK), HTTPStatus.OK
    return jsonify(USER_ALREADY_HAS_ROLE), HTTPStatus.CONFLICT


@users.route("/<user_id>/roles/<role_id>", methods=["DELETE"])
@rate_limit()
@spec.validate(
    resp=SpecResponse(
        HTTP_200=BaseResponseSchema,
        HTTP_403=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["user-role"],
)
def users_delete_role_by_id(user_id, role_id):
    check_uuid(user_id)
    check_uuid(role_id)

    user_from_db = User.query.get_or_404(user_id)
    role_from_db = Role.query.get_or_404(role_id)
    user_from_db.roles.remove(role_from_db)
    try:
        db.session.commit()
    except IntegrityError as err:
        msg = err._message().split("DETAIL:  ")[1].strip()
        return jsonify({"msg": msg}), HTTPStatus.BAD_REQUEST

    return jsonify(ROLE_REMOVE_OK), HTTPStatus.OK
