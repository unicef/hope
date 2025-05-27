import json
from typing import Any, Dict, Optional

from django.conf import settings

from constance import config

from hct_mis_api.apps.utils.celery_tasks import send_email_task


class MailjetClient:
    """
    Mailjet client to send emails using Mailjet API.
    """

    def __init__(
        self,
        subject: str,
        recipients: list[str],
        mailjet_template_id: Optional[int] = None,
        html_body: Optional[str] = None,
        text_body: Optional[str] = None,
        ccs: Optional[list[str]] = None,
        variables: Optional[Dict[str, Any]] = None,
        from_email: Optional[str] = None,
        from_email_display: Optional[str] = None,
    ) -> None:
        self.mailjet_template_id = mailjet_template_id
        self.html_body = html_body
        self.text_body = text_body
        subject_prefix = settings.EMAIL_SUBJECT_PREFIX
        self.subject = f"[{subject_prefix}] {subject}" if subject_prefix else subject
        self.recipients = settings.CATCH_ALL_EMAIL if settings.CATCH_ALL_EMAIL else recipients
        self.ccs = ccs or []
        self.variables = variables
        self.from_email = from_email or settings.DEFAULT_EMAIL
        self.from_email_display = from_email_display or settings.DEFAULT_EMAIL_DISPLAY
        self.attachments = []

    def _validate_email_data(self) -> None:
        if self.mailjet_template_id and (self.html_body or self.text_body):
            raise ValueError("You cannot use both template and custom email body")
        if not self.mailjet_template_id and not (self.html_body or self.text_body):
            raise ValueError("You need to provide either template or custom email body")
        if self.mailjet_template_id and not self.variables:
            raise ValueError("You need to provide body variables for template email")

    def send_email(self) -> None:
        if not config.ENABLE_MAILJET:
            return

        self._validate_email_data()

        email_body = self._get_email_body()
        attachments = {"Attachments": self.attachments} if self.attachments else {}
        data = {
            "Messages": [
                {
                    "From": {"Email": self.from_email, "Name": self.from_email_display},
                    "Subject": self.subject,
                    "To": [
                        {
                            "Email": recipient,
                        }
                        for recipient in self.recipients
                    ],
                    "Cc": [
                        {
                            "Email": cc,
                        }
                        for cc in self.ccs
                    ],
                    **email_body,
                    **attachments,
                }
            ]
        }
        data_json = json.dumps(data)
        send_email_task.delay(data_json)

    def _get_email_body(self) -> Dict[str, Any]:
        """
        Construct the dictionary with the data responsible for email body,
        built for passed content (html and/or text) or mailjet template (with variables).
        """
        if self.mailjet_template_id:
            return {
                "TemplateID": self.mailjet_template_id,
                "TemplateLanguage": True,
                "Variables": self.variables,
            }
        else:  # Body content provided through html_body and/or text_body
            content = {}
            if self.html_body:
                content["HTMLPart"] = self.html_body
            if self.text_body:
                content["TextPart"] = self.text_body
            return content

    def attach_file(self, attachment: str, filename: str, mimetype: str) -> None:
        new_attachment = [
            {
                "ContentType": mimetype,
                "Filename": filename,
                "Base64Content": attachment,
            }
        ]
        self.attachments.extend(new_attachment)
