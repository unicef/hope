from unittest.mock import MagicMock, patch

import jwt
import pytest
from rest_framework import exceptions

from hope.contrib.auth import JWTAuthentication, JWTToken, JWTUser


def _make_request(auth_header: str | None = None) -> MagicMock:
    request = MagicMock()
    if auth_header is None:
        request.META = {}
    else:
        request.META = {"HTTP_AUTHORIZATION": auth_header}
    return request


class TestJWTAuthentication:
    def test_no_auth_header_returns_none(self) -> None:
        request = _make_request()
        auth = JWTAuthentication()
        result = auth.authenticate(request)
        assert result is None

    def test_non_bearer_auth_returns_none(self) -> None:
        request = _make_request("Basic dXNlcjpwYXNz")
        auth = JWTAuthentication()
        result = auth.authenticate(request)
        assert result is None

    def test_bearer_without_token_raises_error(self) -> None:
        request = _make_request("Bearer")
        auth = JWTAuthentication()
        with pytest.raises(exceptions.AuthenticationFailed, match="no credentials provided"):
            auth.authenticate(request)

    def test_bearer_with_too_many_parts_raises_error(self) -> None:
        request = _make_request("Bearer token1 token2")
        auth = JWTAuthentication()
        with pytest.raises(exceptions.AuthenticationFailed, match="invalid format"):
            auth.authenticate(request)

    def test_empty_auth_header_list_returns_none(self) -> None:
        request = MagicMock()
        request.META = {"HTTP_AUTHORIZATION": ""}
        auth = JWTAuthentication()
        result = auth.authenticate(request)
        assert result is None

    @patch("jwt.decode")
    def test_valid_token_returns_user_and_token(self, mock_decode: MagicMock, settings) -> None:
        settings.VISION_JWT_SECRET = "test-secret"
        mock_decode.return_value = {"grant": "API_READ_ONLY"}

        request = _make_request("Bearer valid.jwt.token")
        auth = JWTAuthentication()
        auth.secret_key_setting = "VISION_JWT_SECRET"
        user, token = auth.authenticate(request)

        assert isinstance(user, JWTUser)
        assert isinstance(token, JWTToken)
        assert token.grants == ["API_READ_ONLY"]
        mock_decode.assert_called_once_with(
            "valid.jwt.token",
            "test-secret",
            algorithms=["HS256"],
            options={"verify_exp": True},
        )

    @patch("jwt.decode")
    def test_valid_token_default_grant(self, mock_decode: MagicMock, settings) -> None:
        settings.VISION_JWT_SECRET = "test-secret"
        mock_decode.return_value = {}

        auth = JWTAuthentication()
        auth.secret_key_setting = "VISION_JWT_SECRET"
        _, token = auth.authenticate_credentials("token")

        assert token.grants == ["API_READ_ONLY"]

    @patch("jwt.decode")
    def test_expired_token_raises_error(self, mock_decode: MagicMock, settings) -> None:
        settings.VISION_JWT_SECRET = "test-secret"
        mock_decode.side_effect = jwt.ExpiredSignatureError()

        auth = JWTAuthentication()
        auth.secret_key_setting = "VISION_JWT_SECRET"
        with pytest.raises(exceptions.AuthenticationFailed, match="JWT has expired"):
            auth.authenticate_credentials("expired.token")

    @patch("jwt.decode")
    def test_invalid_token_raises_error(self, mock_decode: MagicMock, settings) -> None:
        settings.VISION_JWT_SECRET = "test-secret"
        mock_decode.side_effect = jwt.InvalidTokenError()

        auth = JWTAuthentication()
        auth.secret_key_setting = "VISION_JWT_SECRET"
        with pytest.raises(exceptions.AuthenticationFailed, match="Invalid JWT token"):
            auth.authenticate_credentials("invalid.token")

    def test_jwt_user_str(self) -> None:
        assert str(JWTUser()) == "jwt-user"

    def test_jwt_user_attributes(self) -> None:
        user = JWTUser()
        assert user.is_authenticated is True
        assert user.is_active is True
        assert user.pk == 0

    def test_jwt_token_attributes(self) -> None:
        token = JWTToken(grants=["read", "write"])
        assert token.grants == ["read", "write"]
