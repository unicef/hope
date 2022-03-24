import logging

from concurrency.api import disable_concurrency

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task()
def recalculate_population_fields_task():
    logger.info("recalculate_population_fields")
    try:
        from hct_mis_api.apps.household.models import Household, Individual, YES

        for hh in (
            Household.objects.filter(collect_individual_data=YES)
            .only("id", "collect_individual_data")
            .prefetch_related("individuals")
            .iterator(chunk_size=10000)
        ):
            with disable_concurrency(Household):
                with disable_concurrency(Individual):
                    hh.recalculate_data()

    except Exception as e:
        logger.exception(e)
        raise

    logger.info("recalculate_population_fields end")
