import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
def send_target_population_task(target_population_id):
    try:
        from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import (
            SendTPToDatahubTask,
        )
        from hct_mis_api.apps.targeting.models import TargetPopulation

        target_population = TargetPopulation.objects.select_related("program").get(id=target_population_id)
        return SendTPToDatahubTask().execute(target_population)
    except Exception as e:
        logger.exception(e)
        raise
