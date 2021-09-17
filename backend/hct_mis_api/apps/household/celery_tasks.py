import logging

from concurrency.exceptions import RecordModifiedError

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task()
def recalculate_population_fields_task():
    logger.info("recalculate_population_fields")

    try:
        from hct_mis_api.apps.household.models import Household

        for hh in Household.objects.all():
            recalculate_household_data(hh)
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("recalculate_population_fields end")


def recalculate_household_data(household, retry=True):
    try:
        household.recalculate_data()
    except RecordModifiedError:
        recalculate_error_handler(household, retry)


def recalculate_error_handler(household, retry):
    if not retry:
        raise
    household.refresh_from_db()
    recalculate_household_data(household, False)
