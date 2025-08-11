import requests

from hope.apps.core.celery import app
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags
from hope.config import settings


@app.task
@log_start_and_end
@sentry_tags
def send_email_task(data_json: str) -> None:
    res = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
        data=data_json,
        timeout=30,
    )
    if res.status_code != 200:
        raise Exception(f"Failed to send email: {res.json()}. Data: {data_json}")
