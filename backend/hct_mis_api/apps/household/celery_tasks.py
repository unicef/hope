import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import XLSXKoboTemplate
from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import KoboRetriableError

logger = logging.getLogger(__name__)


@app.task()
def recalculate_population_fields_task():
    logger.info("recalculate_population_fields")

    try:
        from hct_mis_api.apps.household.models import Household
        for hh in Household.objects.all():
            hh.recalculate_data()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("upload_new_kobo_template_and_update_flex_fields_task_with_retry end")



