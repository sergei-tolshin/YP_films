from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_pydantic_spec import Response
from sqlalchemy.exc import IntegrityError

from api.v1.schema import BaseResponseSchema, spec
from api.v1.schema.role import (RoleListResponseSchema, RoleRequestSchema,
                                RoleResponseSchema, RoleUpdateRequestSchema)
from api.v1.utils import check_uuid
from core.permissions import is_admin
from core.rate_limit import rate_limit
from models import Role
from services.db import db

roles = Blueprint("roles", __name__)

ROLE_DELETE_OK = {"msg": "Role delete successfuly."}
ROLE_UPDATE_OK = {"msg": "Role updated successfuly."}
PERMISSION_DENIED = {"msg": "Permission denied"}


@roles.route("/", methods=["GET"])
@rate_limit()
@jwt_required()
@spec.validate(
    resp=Response(HTTP_200=RoleListResponseSchema, HTTP_400=BaseResponseSchema),
    tags=["roles"],
)
@rate_limit(rpm=50, kind="user")
def get_list():
    roles_queryset = Role.query.all()
    roles_list = RoleListResponseSchema(roles=roles_queryset)
    return jsonify(roles_list.dict())


@roles.route("/", methods=["POST"])
@rate_limit()
@jwt_required()
@spec.validate(
    body=RoleRequestSchema,
    resp=Response(HTTP_200=RoleResponseSchema, HTTP_400=BaseResponseSchema),
    tags=["roles"],
)
@rate_limit(rpm=50, kind="user")
@is_admin()
def create_role():
    data = request.get_json()
    role = Role(**data)
    db.session.add(role)
    try:
        db.session.commit()
    except IntegrityError as err:
        msg = err._message().split("DETAIL:  ")[1].strip()
        return jsonify({"msg": msg}), HTTPStatus.BAD_REQUEST
    response = RoleResponseSchema.from_orm(role)
    return jsonify(response.dict()), HTTPStatus.CREATED


@roles.route("/<role_id>", methods=["GET"])
@rate_limit()
@jwt_required()
@spec.validate(
    resp=Response(
        HTTP_200=RoleResponseSchema,
        HTTP_400=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["roles"],
)
@rate_limit(rpm=50, kind="user")
@is_admin()
def get_role_by_id(role_id):
    check_uuid(role_id)
    role = Role.query.get_or_404(role_id)
    response = RoleResponseSchema.from_orm(role)

    return jsonify(response.dict()), HTTPStatus.OK


@roles.route("/<role_id>", methods=["PATCH"])
@rate_limit()
@spec.validate(
    body=RoleUpdateRequestSchema,
    resp=Response(
        HTTP_200=RoleResponseSchema,
        HTTP_400=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["roles"],
)
@jwt_required()
@rate_limit(rpm=50, kind="user")
@is_admin()
def patch_role_by_id(role_id):
    check_uuid(role_id)
    data = request.get_json()
    role_from_db = Role.query.get_or_404(role_id)
    role = RoleResponseSchema.from_orm(role_from_db)

    fields_to_update = [value for value in data.keys() if value in role.__fields__]

    for field in fields_to_update:
        setattr(role, field, data[field])

    for field in fields_to_update:
        value_to_update = getattr(role, field)
        setattr(role_from_db, field, value_to_update)

    try:
        db.session.commit()
    except IntegrityError as err:
        msg = err._message().split("DETAIL:  ")[1].strip()
        return jsonify({"msg": msg}), HTTPStatus.BAD_REQUEST

    return jsonify(role.dict()), HTTPStatus.OK


@roles.route("/<role_id>", methods=["DELETE"])
@rate_limit()
@jwt_required()
@spec.validate(
    resp=Response(
        HTTP_200=BaseResponseSchema,
        HTTP_400=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["roles"],
)
@rate_limit(rpm=50, kind="user")
@is_admin()
def delete_role_by_id(role_id):
    check_uuid(role_id)
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    try:
        db.session.commit()
    except IntegrityError as err:
        msg = err._message().split("DETAIL:  ")[1].strip()
        return jsonify({"msg": msg}), HTTPStatus.BAD_REQUEST
    return jsonify(ROLE_DELETE_OK)
