import logging

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task
def send_target_population_task(target_population_id):
    logger.info("send_target_population_task start")

    try:
        from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import (
            SendTPToDatahubTask,
        )
        from hct_mis_api.apps.targeting.models import TargetPopulation
        target_population = TargetPopulation.objects.select_related("program").get(id=target_population_id)
        SendTPToDatahubTask().execute(target_population)
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("send_target_population_task end")
