import logging

from hct_mis_api.config.celery import app

logger = logging.getLogger(__name__)


@app.task
def get_sync_run_rapid_pro_task():
    logger.info(f"get_sync_run_rapid_pro_task start")

    try:
        from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import CheckRapidProVerificationTask

        CheckRapidProVerificationTask().execute()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info(f"get_sync_run_rapid_pro_task end")
