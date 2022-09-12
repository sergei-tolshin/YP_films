from .base import BaseOrJSONModel


class LoginBodySchema(BaseOrJSONModel):
    login: str
    password: str
