import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.exchange_rates.utils import fix_exchange_rates
from hct_mis_api.apps.utils.logs import log_start_and_end

logger = logging.getLogger(__name__)


@app.task(queue="priority")
@log_start_and_end
def pull_from_cashassist_datahub_task():
    try:
        from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
            PullFromDatahubTask,
        )

        PullFromDatahubTask().execute()
    except Exception as e:
        logger.exception(e)
        raise


@app.task(queue="priority")
def fix_exchange_rates_task():
    try:
        fix_exchange_rates()
    except Exception as e:
        logger.exception(e)
        raise
