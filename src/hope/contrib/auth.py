from typing import Any

from django.conf import settings
import jwt
from rest_framework import authentication, exceptions

from hope.models.grant import Grant


class JWTUser:
    is_authenticated: bool = True
    is_active: bool = True
    pk: int = 0

    def __str__(self) -> str:
        return "jwt-user"


class JWTToken:
    def __init__(self, grants: list[str]) -> None:
        self.grants = grants


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"
    secret_key_setting: str = ""

    def authenticate(self, request: Any) -> tuple[JWTUser, JWTToken] | None:
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed("Invalid JWT header - no credentials provided")
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed("Invalid JWT header - invalid format")

        token = auth[1].decode()
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token: str) -> tuple[JWTUser, JWTToken]:
        secret = getattr(settings, self.secret_key_setting)
        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={"verify_exp": True},
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("JWT has expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid JWT token")

        grant_name = payload.get("grant", Grant.API_READ_ONLY.name)
        return JWTUser(), JWTToken(grants=[grant_name])
