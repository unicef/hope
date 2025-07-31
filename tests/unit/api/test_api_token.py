import json
from datetime import datetime
from typing import Any
from unittest.mock import patch

from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase, override_settings

from constance.test import override_config
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from unit.api.factories import APITokenFactory

from hct_mis_api.admin.api_token import TOKEN_INFO_EMAIL, APITokenAdmin
from hct_mis_api.api.models import Grant


class TestApiToken(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.afg = create_afghanistan()
        cls.user = UserFactory(
            email="testapitoken@email.com",
        )
        cls.token = APITokenFactory(
            user=cls.user,
            grants=[
                Grant.API_READ_ONLY.name,
                Grant.API_RDI_UPLOAD.name,
                Grant.API_PROGRAM_CREATE.name,
            ],
            valid_to=datetime(2050, 1, 1),
        )
        cls.token.valid_for.set([cls.afg])

    @patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @patch.object(APITokenAdmin, "message_user", return_value=None)
    @patch.object(APITokenAdmin, "__init__", return_value=None)
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_send_api_token(
        self, mocked_requests_init: Any, mocked_requests_user: Any, mocked_requests_post: Any
    ) -> None:
        request = HttpRequest()

        APITokenAdmin()._send_token_email(request, self.token, TOKEN_INFO_EMAIL)

        mocked_requests_post.assert_called_once()

        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {"Email": settings.DEFAULT_EMAIL, "Name": settings.DEFAULT_EMAIL_DISPLAY},
                        "Subject": f"[test] HOPE API Token {self.token} infos",
                        "To": [
                            {
                                "Email": "testapitoken@email.com",
                            },
                        ],
                        "Cc": [],
                        "TextPart": f"\nDear {self.user.first_name},\n\nplease find below API token infos\n\nName: {self.token}\nKey: {self.token.key}\nGrants: {self.token.grants}\nExpires: {self.token.valid_to}\nBusiness Areas: {', '.join(self.token.valid_for.values_list('name', flat=True))}\n\nRegards\n\nThe HOPE Team\n",
                    }
                ]
            }
        )
        mocked_requests_post.assert_called_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
        )
