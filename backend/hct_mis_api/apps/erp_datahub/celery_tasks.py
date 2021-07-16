import logging

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task
def sync_to_mis_datahub_task():
    logger.info("sync_to_mis_datahub_task start")

    try:
        from hct_mis_api.apps.erp_datahub.tasks.sync_to_mis_datahub import SyncToMisDatahubTask

        SyncToMisDatahubTask().execute()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("sync_to_mis_datahub_task end")
