from .base import BaseOrJSONModel


class CookieSchema(BaseOrJSONModel):
    access_token_cookie: str | None = None
