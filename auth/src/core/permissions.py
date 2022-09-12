from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity
from werkzeug.exceptions import Forbidden

from models.user import User


def has_all_roles(roles: list):
    """
    Check that user has all roles required by an endpoint
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            jwt = get_jwt()
            user_roles = jwt.get("rol", [])
            is_superuser = jwt.get("is_superuser")
            if any((is_superuser, set(roles).issubset(user_roles))):
                return func(*args, **kwargs)
            raise Forbidden("You do not have access")

        return inner

    return wrapper


def has_any_roles(roles: list):
    """
    Check that user has at least a role required by an endpoint
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            jwt = get_jwt()
            user_roles = jwt.get("rol", [])
            is_superuser = jwt.get("is_superuser")
            if any((is_superuser, set(roles).intersection(user_roles), not roles)):
                return func(*args, **kwargs)
            raise Forbidden("You do not have access")

        return inner

    return wrapper


def user_or_admin():
    """
    Check that user_id is the same in url and in jwt.
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            jwt = get_jwt()
            is_superuser = jwt.get("is_superuser")

            identity = get_jwt_identity()
            user_id = kwargs["user_id"]
            user = User.query.filter_by(username=identity).first()

            if any((is_superuser, user_id == str(user.uuid))):
                return func(*args, **kwargs)
            raise Forbidden("You do not have access")

        return inner

    return wrapper


def is_admin():
    """
    Check is superuser.
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            jwt = get_jwt()
            is_superuser = jwt.get("is_superuser")

            if is_superuser:
                return func(*args, **kwargs)
            raise Forbidden("You do not have access")

        return inner

    return wrapper
