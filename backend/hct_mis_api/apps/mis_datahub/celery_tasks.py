import logging
from typing import Any, Dict
from uuid import UUID

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def send_target_population_task(self: Any, target_population_id: UUID) -> Dict:
    try:
        from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import (
            SendTPToDatahubTask,
        )
        from hct_mis_api.apps.targeting.models import TargetPopulation

        target_population = TargetPopulation.objects.select_related("program").get(id=target_population_id)
        set_sentry_business_area_tag(target_population.business_area.name)
        return SendTPToDatahubTask().execute(target_population)
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
