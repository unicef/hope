import logging
from uuid import UUID

from concurrency.api import disable_concurrency

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task()
def recalculate_population_fields_task(household_ids: list[UUID] = None):
    logger.info("recalculate_population_fields")
    try:
        from hct_mis_api.apps.household.models import YES, Household, Individual

        params = {"collect_individual_data": YES}

        if household_ids:
            params["pk__in"] = household_ids

        for hh in (
            Household.objects.filter(**params)
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
