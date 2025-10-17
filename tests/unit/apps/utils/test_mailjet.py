import base64
import io
import json
from typing import Any
from unittest.mock import patch

from constance.test import override_config
from django.conf import settings
from django.test import TestCase, override_settings
from openpyxl import Workbook
import pytest

from extras.test_utils.factories.account import UserFactory
from hope.apps.utils.mailjet import MailjetClient


class TestMailjet(TestCase):
    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_body_with_template(self, mocked_requests_post: Any) -> None:
        mocked_requests_post.return_value.status_code = 200
        mailjet = MailjetClient(
            mailjet_template_id=1,
            subject="Subject for email with Template",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
            variables={"key": "value"},
        )
        mailjet.send_email()
        mocked_requests_post.assert_called_once()
        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {
                            "Email": settings.DEFAULT_EMAIL,
                            "Name": settings.DEFAULT_EMAIL_DISPLAY,
                        },
                        "Subject": "[test] Subject for email with Template",
                        "To": [
                            {
                                "Email": "test@email.com",
                            },
                            {
                                "Email": "test2@email.com",
                            },
                        ],
                        "Cc": [
                            {
                                "Email": "testcc@email.com",
                            }
                        ],
                        "TemplateID": 1,
                        "TemplateLanguage": True,
                        "Variables": {"key": "value"},
                    }
                ]
            }
        )

        mocked_requests_post.assert_called_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
            timeout=30,
        )

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_settings(
        EMAIL_SUBJECT_PREFIX="test",
        CATCH_ALL_EMAIL=["catchallemail@email.com", "catchallemail2@email.com"],
    )
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_body_with_template_with_catch_all(self, mocked_requests_post: Any) -> None:
        mocked_requests_post.return_value.status_code = 200
        mailjet = MailjetClient(
            mailjet_template_id=1,
            subject="Subject for email with Template for Catch All",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
            variables={"key": "value"},
        )
        mailjet.send_email()
        mocked_requests_post.assert_called_once()
        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {
                            "Email": settings.DEFAULT_EMAIL,
                            "Name": settings.DEFAULT_EMAIL_DISPLAY,
                        },
                        "Subject": "[test] Subject for email with Template for Catch All",
                        "To": [
                            {
                                "Email": "catchallemail@email.com",
                            },
                            {
                                "Email": "catchallemail2@email.com",
                            },
                        ],
                        "Cc": [
                            {
                                "Email": "testcc@email.com",
                            }
                        ],
                        "TemplateID": 1,
                        "TemplateLanguage": True,
                        "Variables": {"key": "value"},
                    }
                ]
            }
        )

        mocked_requests_post.assert_called_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
            timeout=30,
        )

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_body_with_html_and_text_body(self, mocked_requests_post: Any) -> None:
        mocked_requests_post.return_value.status_code = 200
        mailjet = MailjetClient(
            html_body="<h1>HTML Body</h1>",
            text_body="Text Body",
            subject="Subject for email with HTML and Text body",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
        )
        mailjet.send_email()
        mocked_requests_post.assert_called_once()
        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {
                            "Email": settings.DEFAULT_EMAIL,
                            "Name": settings.DEFAULT_EMAIL_DISPLAY,
                        },
                        "Subject": "[test] Subject for email with HTML and Text body",
                        "To": [
                            {
                                "Email": "test@email.com",
                            },
                            {
                                "Email": "test2@email.com",
                            },
                        ],
                        "Cc": [
                            {
                                "Email": "testcc@email.com",
                            }
                        ],
                        "HTMLPart": "<h1>HTML Body</h1>",
                        "TextPart": "Text Body",
                    }
                ]
            }
        )

        mocked_requests_post.assert_called_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
            timeout=30,
        )

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_body_with_text_body(self, mocked_requests_post: Any) -> None:
        mocked_requests_post.return_value.status_code = 200
        mailjet = MailjetClient(
            text_body="Text Body",
            subject="Subject for email with Text body",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
        )
        mailjet.send_email()
        mocked_requests_post.assert_called_once()
        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {
                            "Email": settings.DEFAULT_EMAIL,
                            "Name": settings.DEFAULT_EMAIL_DISPLAY,
                        },
                        "Subject": "[test] Subject for email with Text body",
                        "To": [
                            {
                                "Email": "test@email.com",
                            },
                            {
                                "Email": "test2@email.com",
                            },
                        ],
                        "Cc": [
                            {
                                "Email": "testcc@email.com",
                            }
                        ],
                        "TextPart": "Text Body",
                    }
                ]
            }
        )

        mocked_requests_post.assert_called_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
            timeout=30,
        )

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_body_with_template_and_attachment(self, mocked_requests_post: Any) -> None:
        mocked_requests_post.return_value.status_code = 200
        mailjet = MailjetClient(
            mailjet_template_id=1,
            subject="Subject for email with Template and Attachments",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
            variables={"key": "value"},
        )

        attachment_wb = Workbook()
        attachment_ws = attachment_wb.active
        attachment_ws.title = "File Title"
        attachment_ws.append(["Col1", "Col2", "Col3"])
        attachment_ws.append(["Val1", "Val2", "Val3"])
        buffer = io.BytesIO()
        attachment_wb.save(buffer)
        buffer.seek(0)
        attachment_content = buffer.getvalue()
        base64_encoded_content = base64.b64encode(attachment_content).decode("utf-8")

        mailjet.attach_file(
            attachment=base64_encoded_content,
            filename="filename.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        mailjet.attach_file(
            attachment=base64_encoded_content,
            filename="filename.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        mailjet.send_email()
        mocked_requests_post.assert_called_once()
        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {
                            "Email": settings.DEFAULT_EMAIL,
                            "Name": settings.DEFAULT_EMAIL_DISPLAY,
                        },
                        "Subject": "[test] Subject for email with Template and Attachments",
                        "To": [
                            {
                                "Email": "test@email.com",
                            },
                            {
                                "Email": "test2@email.com",
                            },
                        ],
                        "Cc": [
                            {
                                "Email": "testcc@email.com",
                            }
                        ],
                        "TemplateID": 1,
                        "TemplateLanguage": True,
                        "Variables": {"key": "value"},
                        "Attachments": [
                            {
                                "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                "Filename": "filename.xlsx",
                                "Base64Content": base64_encoded_content,
                            },
                            {
                                "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                "Filename": "filename.xlsx",
                                "Base64Content": base64_encoded_content,
                            },
                        ],
                    }
                ]
            }
        )

        mocked_requests_post.assert_called_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
            timeout=30,
        )

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_incorrect_body_with_template_and_html_body(self, mocked_requests_post: Any) -> None:
        mailjet = MailjetClient(
            html_body="<h1>HTML Body</h1>",
            mailjet_template_id=1,
            subject="Subject for incorrect body",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
            variables={"key": "value"},
        )
        with pytest.raises(ValueError, match="You cannot use both template and custom email body"):
            mailjet.send_email()
        mocked_requests_post.assert_not_called()

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_incorrect_body_with_template_and_text_body(self, mocked_requests_post: Any) -> None:
        mailjet = MailjetClient(
            text_body="Text Body",
            mailjet_template_id=1,
            subject="Subject for incorrect body",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
            variables={"key": "value"},
        )
        with pytest.raises(ValueError, match="You cannot use both template and custom email body"):
            mailjet.send_email()
        mocked_requests_post.assert_not_called()

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_incorrect_body_with_template_and_without_variables(self, mocked_requests_post: Any) -> None:
        mailjet = MailjetClient(
            mailjet_template_id=1,
            subject="Subject for incorrect body",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
        )
        with pytest.raises(ValueError, match="You need to provide body variables for template email"):
            mailjet.send_email()
        mocked_requests_post.assert_not_called()

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_config(ENABLE_MAILJET=True)
    def test_mailjet_incorrect_body_without_template_and_without_html_and_text_body(
        self, mocked_requests_post: Any
    ) -> None:
        mailjet = MailjetClient(
            subject="Subject for incorrect body",
            recipients=["test@email.com", "test2@email.com"],
            ccs=["testcc@email.com"],
        )
        with pytest.raises(ValueError, match="You need to provide either template or custom email body"):
            mailjet.send_email()
        mocked_requests_post.assert_not_called()

    @patch("hope.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_email_user_via_mailjet(self, mocked_requests_post: Any) -> None:
        mocked_requests_post.return_value.status_code = 200
        user = UserFactory(email="testuser@email.com", username="testuser")
        user.email_user(
            subject="Test subject",
            html_body="<h1>HTML Body</h1>",
            from_email="sender@email.com",
            from_email_display="Sender",
            ccs=["testcc@email.com"],
        )
        mocked_requests_post.assert_called_once()
        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {"Email": "sender@email.com", "Name": "Sender"},
                        "Subject": "[test] Test subject",
                        "To": [
                            {
                                "Email": "testuser@email.com",
                            },
                        ],
                        "Cc": [
                            {
                                "Email": "testcc@email.com",
                            }
                        ],
                        "HTMLPart": "<h1>HTML Body</h1>",
                    }
                ]
            }
        )

        mocked_requests_post.assert_called_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
            timeout=30,
        )
