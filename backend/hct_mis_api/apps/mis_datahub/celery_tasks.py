import logging

from hct_mis_api.config.celery import app

logger = logging.getLogger(__name__)


@app.task
def send_target_population_task():
    logger.info("send_target_population_task start")

    try:
        from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask

        SendTPToDatahubTask().execute()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("send_target_population_task end")
