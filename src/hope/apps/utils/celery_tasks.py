import requests

from hope.apps.core.celery import app
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags
from hope.config import settings

# Mailjet was unreachable, rate-limited or faulting; the same payload is worth sending again
RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})


class MailjetSendError(Exception):
    """Mailjet rejected the message, and would reject the same message again."""


class MailjetTemporaryError(MailjetSendError):
    """Mailjet could not take the message this time."""


@app.task(
    autoretry_for=(MailjetTemporaryError, requests.RequestException),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
@log_start_and_end
@sentry_tags
def send_email_async_task(data_json: str) -> None:
    res = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
        data=data_json,
        timeout=30,
    )
    if res.status_code != 200:
        detail = f"Failed to send email: {res.text}. Data: {data_json}"
        if res.status_code in RETRYABLE_STATUS_CODES:
            raise MailjetTemporaryError(detail)
        raise MailjetSendError(detail)
