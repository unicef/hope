import logging

from hct_mis_api.config.celery import app

logger = logging.getLogger(__name__)


@app.task
def pull_from_erp_datahub_task():
    logger.info("pull_from_erp_datahub_task start")

    try:
        from hct_mis_api.apps.erp_datahub.tasks.pull_from_erp_datahub import PullFromErpDatahubTask

        PullFromErpDatahubTask().execute()
    except Exception as e:
        logger.exception(e)

    logger.info("pull_from_erp_datahub_task end")
