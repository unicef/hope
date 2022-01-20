import logging

from concurrency.api import disable_concurrency
from concurrency.exceptions import RecordModifiedError

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task()
def recalculate_population_fields_task():
    logger.info("recalculate_population_fields")

    try:
        from hct_mis_api.apps.household.models import Household, Individual

        for hh in Household.objects.all():
            with disable_concurrency(Household):
                with disable_concurrency(Individual):
                    hh.recalculate_data()

    except Exception as e:
        logger.exception(e)
        raise

    logger.info("recalculate_population_fields end")
