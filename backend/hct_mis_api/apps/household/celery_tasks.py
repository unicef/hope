import logging
from typing import List, Optional
from uuid import UUID

from concurrency.api import disable_concurrency
from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task()
@log_start_and_end
@sentry_tags
def recalculate_population_fields_task(household_ids: Optional[List[UUID]] = None):
    try:
        from hct_mis_api.apps.household.models import Household, Individual

        params = {}
        if household_ids:
            params["pk__in"] = household_ids

        for hh in (
            Household.objects.filter(**params)
            .only("id", "collect_individual_data")
            .prefetch_related("individuals")
            .iterator(chunk_size=10000)
        ):
            with configure_scope() as scope:
                scope.set_tag("business_area", hh.business_area)
                with disable_concurrency(Household), disable_concurrency(Individual):
                    recalculate_data(hh)

    except Exception as e:
        logger.exception(e)
        raise


@app.task()
@sentry_tags
def calculate_children_fields_for_not_collected_individual_data():
    from django.db.models import F

    from hct_mis_api.apps.household.models import Household

    Household.objects.update(
        children_count=F("female_age_group_0_5_count")
        + F("female_age_group_6_11_count")
        + F("female_age_group_12_17_count")
        + F("male_age_group_0_5_count")
        + F("male_age_group_6_11_count")
        + F("male_age_group_12_17_count"),
        female_children_count=F("female_age_group_0_5_count")
        + F("female_age_group_6_11_count")
        + F("female_age_group_12_17_count"),
        male_children_count=F("male_age_group_0_5_count")
        + F("male_age_group_6_11_count")
        + F("male_age_group_12_17_count"),
        children_disabled_count=F("female_age_group_0_5_disabled_count")
        + F("female_age_group_6_11_disabled_count")
        + F("female_age_group_12_17_disabled_count")
        + F("male_age_group_0_5_disabled_count")
        + F("male_age_group_6_11_disabled_count")
        + F("male_age_group_12_17_disabled_count"),
        female_children_disabled_count=F("female_age_group_0_5_disabled_count")
        + F("female_age_group_6_11_disabled_count")
        + F("female_age_group_12_17_disabled_count"),
        male_children_disabled_count=F("male_age_group_0_5_disabled_count")
        + F("male_age_group_6_11_disabled_count")
        + F("male_age_group_12_17_disabled_count"),
    )


@app.task()
@sentry_tags
def update_individuals_iban_from_xlsx_task(xlsx_update_file_id: UUID, uploaded_by_id: UUID):
    from hct_mis_api.apps.account.models import User
    from hct_mis_api.apps.household.models import XlsxUpdateFile
    from hct_mis_api.apps.household.services.individuals_iban_xlsx_update import (
        IndividualsIBANXlsxUpdate,
    )

    uploaded_by = User.objects.get(id=uploaded_by_id)
    try:
        xlsx_update_file = XlsxUpdateFile.objects.get(id=xlsx_update_file_id)
        with configure_scope() as scope:
            scope.set_tag("business_area", xlsx_update_file.business_area)
            updater = IndividualsIBANXlsxUpdate(xlsx_update_file)
            updater.validate()
            if updater.validation_errors:
                updater.send_failure_email()
                return

            updater.update()
            updater.send_success_email()

    except Exception as e:
        IndividualsIBANXlsxUpdate.send_error_email(
            error_message=str(e), xlsx_update_file_id=str(xlsx_update_file_id), uploaded_by=uploaded_by
        )
