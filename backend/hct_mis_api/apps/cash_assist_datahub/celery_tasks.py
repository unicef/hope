import logging
from typing import Any

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.exchange_rates.utils import fix_exchange_rates
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task(bind=True, queue="priority", default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def pull_from_cashassist_datahub_task(self: Any) -> None:
    try:
        from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
            PullFromDatahubTask,
        )

        PullFromDatahubTask().execute()
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, queue="priority", default_retry_delay=60, max_retries=3)
@sentry_tags
def fix_exchange_rates_task(self: Any) -> None:
    try:
        fix_exchange_rates()
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
