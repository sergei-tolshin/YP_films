from authlib.integrations.flask_client import OAuth

from core import config

oauth = OAuth()
oauth.register(
    name=config.OAuthServiceNames.google.value,
    server_metadata_url=config.OAUTH_GOOGLE_CONF_URL,
    client_kwargs=config.OAUTH_GOOGLE_CLIENT_KWARGS
)
oauth.register(
    name=config.OAuthServiceNames.yandex.value,
    authorize_url=config.OAUTH_YANDEX_AUTTHORIZE_URL,
    authorize_params=config.OAUTH_YANDEX_AUTTHORIZE_PARAMS,
    access_token_url=config.OAUTH_YANDEX_TOKEN_URL,
    access_token_params=config.OAUTH_YANDEX_TOKEN_PARAMS,
    userinfo_endpoint=config.OAUTH_YANDEX_USERINFO_ENDPOINT,
    client_kwargs=config.OAUTH_YANDEX_CLIENT_KWARGS
)


def init_oauth(app):
    oauth.init_app(app)
