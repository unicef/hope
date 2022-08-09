import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
@sentry_tags
def sync_to_mis_datahub_task():
    try:
        from hct_mis_api.apps.erp_datahub.tasks.sync_to_mis_datahub import (
            SyncToMisDatahubTask,
        )

        SyncToMisDatahubTask().execute()
    except Exception as e:
        logger.exception(e)
        raise
