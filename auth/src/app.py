import sentry_sdk
from flask import Flask, request, has_request_context
from flask.logging import default_handler
from flask_jwt_extended import JWTManager
from pythonjsonlogger import jsonlogger
from sentry_sdk.integrations.flask import FlaskIntegration

from api.v1 import auth, roles, users, inside_api
from api.v1.schema import spec
from core.config import SENTRY_DSN
from services.db import init_db
from services.jaeger import init_jaeger
from services.oauth import init_oauth
from services.redis import init_redis

jwt = JWTManager()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if has_request_context():
            log_record['request_id'] = request.headers.get('X-Request-Id')
            log_record['url'] = request.url
        else:
            log_record['request_id'] = None
            log_record['url'] = None


formatter = CustomJsonFormatter('%(asctime)s %(request_id)s %(url)s %(name)s %(levelname)s %(message)s')


def create_app(test_config=None):
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FlaskIntegration(), ])
    app = Flask(__name__)
    default_handler.setFormatter(formatter)
    app.secret_key = "super_secret_key"
    if test_config is None:
        app.config.from_pyfile("core/config.py")
    else:
        app.config.from_mapping(test_config)
    init_db(app)
    init_redis(app)
    init_oauth(app)
    jwt.init_app(app)
    init_jaeger(app)

    app.register_blueprint(auth, url_prefix="/auth/api/v1/auth")
    app.register_blueprint(roles, url_prefix="/auth/api/v1/roles")
    app.register_blueprint(users, url_prefix="/auth/api/v1/users")
    app.register_blueprint(inside_api, url_prefix="/inside_api")
    spec.register(app)
    if app.config["JAEGER_ON"]:
        @app.before_request
        def before_request():
            request_id = request.headers.get("X-Request-Id")
            if not request_id:
                raise RuntimeError("request id is requred")

    return app

# if __name__ == '__main__':
#     app = create_app()
#     app.run()
