import requests

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags
from hct_mis_api.config import settings


@app.task
@log_start_and_end
@sentry_tags
def send_email_task(data_json: str) -> None:
    res = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
        data=data_json,
    )
    if res.status_code != 200:
        raise Exception(f"Failed to send email: {res.json()}. Data: {data_json}")
