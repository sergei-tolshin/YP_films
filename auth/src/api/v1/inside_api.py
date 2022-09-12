from flask import Blueprint, jsonify
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from flask_pydantic_spec import Response as SpecResponse

from api.v1.schema import BaseResponseSchema, spec
from api.v1.schema.role import RoleListResponseSchema
from core.rate_limit import rate_limit
from models.user import User

inside_api = Blueprint("inside_api", __name__)


@inside_api.route("/get-permission-level", methods=["GET"])
@rate_limit()
@spec.validate(
    resp=SpecResponse(
        HTTP_200=RoleListResponseSchema,
        HTTP_403=BaseResponseSchema,
        HTTP_404=BaseResponseSchema,
    ),
    tags=["user-role"],
)
@jwt_required()
def users_get_my_roles_by_id():
    user = User.query.filter_by(username=get_jwt_identity()).first()
    roles_list = user.roles
    permission_level = max(role.permission_level for role in roles_list) if roles_list else 0
    roles = RoleListResponseSchema(roles=roles_list, permission_level=permission_level)
    return jsonify(roles.dict())
