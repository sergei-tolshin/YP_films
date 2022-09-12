from datetime import datetime
from functools import wraps

from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import TooManyRequests

from services.redis import redis_client

RATE_LIMIT_PREFIX = "rate-limit"


def rate_limit(rpm: int = 10000, kind: str = "all"):
    """
    Rate-limit function.
    :param kind: "all" or "user".
    :param rpm: max quantity per minute.
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            match kind:
                case "all":
                    keys_pattern = f"{RATE_LIMIT_PREFIX}_{func.__name__}"
                case "user":
                    keys_pattern = f"{RATE_LIMIT_PREFIX}_{get_jwt_identity}"
            keys_count = len(list(redis_client.scan_iter(match=f"{keys_pattern}*")))
            if keys_count < rpm:
                redis_client.setex(f"""{keys_pattern}_{datetime.now().strftime("%M%f")}""", 60, 1)
                return func(*args, **kwargs)
            raise TooManyRequests("Easy")

        return inner

    return wrapper
