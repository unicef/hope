import json
from typing import Any, Dict, Optional

from django.conf import settings

import requests
from constance import config


class MailjetClient:
    """
    Mailjet client to send emails using Mailjet API.
    """

    def __init__(
        self,
        mailjet_template_id: int,
        subject: str,
        recipients: list[str],
        ccs: Optional[list[str]] = None,
        variables: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.mailjet_template_id = mailjet_template_id
        self.subject = subject
        self.recipients = recipients
        self.ccs = ccs or []
        self.variables = variables

    def send_email(self) -> bool:
        if not config.ENABLE_MAILJET:
            return False
        data = {
            "Messages": [
                {
                    "From": {"Email": settings.EMAIL_HOST_USER, "Name": settings.DEFAULT_FROM_EMAIL},
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
                    "TemplateID": self.mailjet_template_id,
                    "TemplateLanguage": True,
                    "Variables": self.variables,
                }
            ]
        }
        data_json = json.dumps(data)
        res = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=data_json,
        )
        return res.status_code == 200
