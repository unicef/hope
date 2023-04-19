import logging
from typing import Any

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def sync_to_mis_datahub_task(self: Any) -> None:
    try:
        from hct_mis_api.apps.erp_datahub.tasks.sync_to_mis_datahub import (
            SyncToMisDatahubTask,
        )

        SyncToMisDatahubTask().execute()
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
