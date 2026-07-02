from datetime import datetime
import json
from unittest.mock import MagicMock, patch

from constance.test import override_config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import override_settings
import pytest

from extras.test_utils.factories import UserFactory
from extras.test_utils.factories.api import APITokenFactory
from hope.admin.api_token import TOKEN_INFO_EMAIL, APITokenAdmin
from hope.models import APIToken
from hope.models.grant import Grant

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return UserFactory(email="testapitoken@email.com")


@pytest.fixture
def token(user, afghanistan) -> APIToken:
    token = APITokenFactory(
        user=user,
        grants=[
            Grant.API_READ_ONLY.name,
            Grant.API_RDI_UPLOAD.name,
            Grant.API_PROGRAM_CREATE.name,
        ],
        valid_to=datetime(2050, 1, 1),
    )
    token.valid_for.set([afghanistan])
    return token


@patch("hope.apps.utils.celery_tasks.requests.post")
@patch("hope.admin.api_token.publish_rendered_email_notification")
@patch.object(APITokenAdmin, "message_user", return_value=None)
@patch.object(APITokenAdmin, "__init__", return_value=None)
@override_settings(EMAIL_SUBJECT_PREFIX="test")
@override_config(ENABLE_MAILJET=True)
def test_send_api_token(
    mocked_admin_init: MagicMock,
    mocked_message_user: MagicMock,
    mocked_publish_rendered_email_notification: MagicMock,
    mocked_requests_post: MagicMock,
    token: APIToken,
    user: User,
) -> None:
    request = HttpRequest()

    APITokenAdmin()._send_token_email(request, token, TOKEN_INFO_EMAIL)

    mocked_requests_post.assert_called_once()

    mocked_requests_post.assert_called_with(
        "https://api.mailjet.com/v3.1/send",
        auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
        data=mocked_requests_post.call_args.kwargs["data"],
        timeout=30,
    )
    actual_data = json.loads(mocked_requests_post.call_args.kwargs["data"])
    message = actual_data["Messages"][0]
    assert message["From"] == {
        "Email": settings.DEFAULT_EMAIL,
        "Name": settings.DEFAULT_EMAIL_DISPLAY,
    }
    assert message["Subject"] == f"[test] HOPE API Token {token} infos"
    assert message["To"] == [{"Email": "testapitoken@email.com"}]
    assert message["Cc"] == []
    assert f"Dear {user.first_name or user.username}" in message["TextPart"]
    assert "please find below API token infos" in message["TextPart"]
    assert f"Key: {token.key}" in message["TextPart"]
    assert f"<p>Dear {user.first_name or user.username},</p>" in message["HTMLPart"]
    assert f"Key: {token.key}<br>" in message["HTMLPart"]
    notification = mocked_publish_rendered_email_notification.call_args.args[0]
    assert notification.user == user
    assert notification.subject == f"HOPE API Token {token} infos"
    assert notification.context["token_key"] == token.key
    assert notification.context["show_token_key"] is True
