import datetime

from flask import Flask
from flask_redis import FlaskRedis


class RedisTokenRevokeStorage:

    def __init__(self, client: FlaskRedis, flask_app: Flask) -> None:
        self.expire_secs = flask_app.config['JWT_REFRESH_TOKEN_EXPIRES'] * 1.2
        self.redis = client

    def add_token(self, token: str) -> None:
        self.redis.setex(token, self.expire_secs, datetime.datetime.utcnow().timestamp())

    def check_token(self, token: str) -> bool:
        result = self.redis.get(token)
        return not result


class RedisLogoutAllDevicesStorage:

    def __init__(self, client: FlaskRedis, flask_app: Flask) -> None:
        self.expire_secs = flask_app.config['JWT_REFRESH_TOKEN_EXPIRES'] * 2.5
        self.redis = client

    def set(self, identity: str) -> None:
        self.redis.setex(identity, self.expire_secs, float(datetime.datetime.utcnow().timestamp()))

    def check_logout_all(self, jwt: dict) -> datetime:
        """
        True when token is not valid: older then logout all entry.
        """
        iat = jwt['iat']
        timestamp = self.redis.get(jwt['jti']) or 0
        return iat < timestamp


redis_client = FlaskRedis()


def init_redis(app):
    redis_client.init_app(app)
