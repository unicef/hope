import logging

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task
def pull_from_cashassist_datahub_task():
    logger.info("pull_from_cashassist_datahub_task start")

    try:
        from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import PullFromDatahubTask

        PullFromDatahubTask().execute()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("pull_from_cashassist_datahub_task end")
