import hashlib
import json
import logging
from typing import List, Optional
from uuid import UUID

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from concurrency.api import disable_concurrency
from constance import config

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.household.documents import HouseholdDocument, get_individual_doc
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_FULL,
    COLLECT_TYPE_PARTIAL,
    Household,
    Individual,
)
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.utils import enroll_households_to_program
from hct_mis_api.apps.utils.elasticsearch_utils import populate_index
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.phone import calculate_phone_numbers_validity
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task()
@log_start_and_end
@sentry_tags
def recalculate_population_fields_chunk_task(households_ids: List[UUID], program_id: Optional[str] = None) -> None:
    from hct_mis_api.apps.household.models import Household, Individual

    # memory optimization
    paginator = Paginator(households_ids, 200)

    with disable_concurrency(Household), disable_concurrency(Individual):
        program = Program.objects.get(id=program_id) if program_id else None
        with transaction.atomic():
            for page in paginator.page_range:
                logger.info(
                    f"recalculate_population_fields_chunk_task: Processing page {page} of {paginator.num_pages}"
                )
                households_ids_page = paginator.page(page).object_list
                households_to_update = []
                fields_to_update = []
                for hh in (
                    Household.objects.filter(pk__in=households_ids_page)
                    .only("id", "collect_individual_data")
                    .prefetch_related("individuals")
                    .select_for_update(of=("self",), skip_locked=True)
                    .order_by("pk")
                ):
                    if program:
                        hh.program = program
                    set_sentry_business_area_tag(hh.business_area.name)
                    household, updated_fields = recalculate_data(hh, save=False)
                    households_to_update.append(household)
                    fields_to_update.extend(x for x in updated_fields if x not in fields_to_update)
                if fields_to_update:
                    Household.objects.bulk_update(households_to_update, fields_to_update)


@app.task()
@log_start_and_end
@sentry_tags
def recalculate_population_fields_task(
    household_ids: Optional[List[str]] = None, program_id: Optional[str] = None
) -> None:
    from hct_mis_api.apps.household.models import Household

    params = {}
    if household_ids:
        params["pk__in"] = household_ids
    recalculate_composition = None
    if program_id:
        program = Program.objects.get(id=program_id)
        recalculate_composition = program.data_collecting_type.recalculate_composition
    queryset = Household.objects.filter(**params).only("pk").order_by("pk")
    if recalculate_composition is None:
        queryset = queryset.filter(collect_individual_data__in=(COLLECT_TYPE_FULL, COLLECT_TYPE_PARTIAL))
    elif not recalculate_composition:
        queryset = queryset.none()

    if queryset.exists():
        paginator = Paginator(queryset, config.RECALCULATE_POPULATION_FIELDS_CHUNK)

        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            recalculate_population_fields_chunk_task.delay(
                households_ids=list(page.object_list.values_list("pk", flat=True)), program_id=program_id
            )


@app.task()
@log_start_and_end
@sentry_tags
def interval_recalculate_population_fields_task() -> None:
    from hct_mis_api.apps.household.models import Individual

    datetime_now = timezone.now()
    now_day, now_month = datetime_now.day, datetime_now.month

    households = (
        Individual.objects.filter(birth_date__day=now_day, birth_date__month=now_month)
        .values_list("household_id", flat=True)
        .distinct()
    )

    recalculate_population_fields_task.delay(household_ids=list(households))


@app.task()
@log_start_and_end
@sentry_tags
def calculate_children_fields_for_not_collected_individual_data() -> int:
    from django.db.models.functions import Coalesce

    from hct_mis_api.apps.household.models import (
        COLLECT_TYPE_FULL,
        COLLECT_TYPE_PARTIAL,
        Household,
    )

    return Household.objects.exclude(collect_individual_data__in=[COLLECT_TYPE_FULL, COLLECT_TYPE_PARTIAL]).update(
        children_count=Coalesce("female_age_group_0_5_count", 0)
        + Coalesce("female_age_group_6_11_count", 0)
        + Coalesce("female_age_group_12_17_count", 0)
        + Coalesce("male_age_group_0_5_count", 0)
        + Coalesce("male_age_group_6_11_count", 0)
        + Coalesce("male_age_group_12_17_count", 0),
        female_children_count=Coalesce("female_age_group_0_5_count", 0)
        + Coalesce("female_age_group_6_11_count", 0)
        + Coalesce("female_age_group_12_17_count", 0),
        male_children_count=Coalesce("male_age_group_0_5_count", 0)
        + Coalesce("male_age_group_6_11_count", 0)
        + Coalesce("male_age_group_12_17_count", 0),
        children_disabled_count=Coalesce("female_age_group_0_5_disabled_count", 0)
        + Coalesce("female_age_group_6_11_disabled_count", 0)
        + Coalesce("female_age_group_12_17_disabled_count", 0)
        + Coalesce("male_age_group_0_5_disabled_count", 0)
        + Coalesce("male_age_group_6_11_disabled_count", 0)
        + Coalesce("male_age_group_12_17_disabled_count", 0),
        female_children_disabled_count=Coalesce("female_age_group_0_5_disabled_count", 0)
        + Coalesce("female_age_group_6_11_disabled_count", 0)
        + Coalesce("female_age_group_12_17_disabled_count", 0),
        male_children_disabled_count=Coalesce("male_age_group_0_5_disabled_count", 0)
        + Coalesce("male_age_group_6_11_disabled_count", 0)
        + Coalesce("male_age_group_12_17_disabled_count", 0),
    )


@app.task()
@log_start_and_end
@sentry_tags
def update_individuals_iban_from_xlsx_task(xlsx_update_file_id: UUID, uploaded_by_id: UUID) -> None:
    from hct_mis_api.apps.account.models import User
    from hct_mis_api.apps.household.models import XlsxUpdateFile
    from hct_mis_api.apps.household.services.individuals_iban_xlsx_update import (
        IndividualsIBANXlsxUpdate,
    )

    uploaded_by = User.objects.get(id=uploaded_by_id)
    xlsx_update_file = XlsxUpdateFile.objects.get(id=xlsx_update_file_id)
    enable_email_notification = xlsx_update_file.business_area.enable_email_notification
    try:
        set_sentry_business_area_tag(xlsx_update_file.business_area.name)
        updater = IndividualsIBANXlsxUpdate(xlsx_update_file)
        updater.validate()
        if updater.validation_errors and enable_email_notification:
            updater.send_failure_email()
            return

        updater.update()
        if enable_email_notification:
            updater.send_success_email()

    except Exception as e:
        if enable_email_notification:
            IndividualsIBANXlsxUpdate.send_error_email(
                error_message=str(e), xlsx_update_file_id=str(xlsx_update_file_id), uploaded_by=uploaded_by
            )


@app.task()
@log_start_and_end
@sentry_tags
def revalidate_phone_number_task(individual_ids: List[UUID]) -> None:
    individuals_to_update = []
    individuals = Individual.objects.filter(pk__in=individual_ids).only("phone_no", "phone_no_alternative")
    for individual in individuals:
        individuals_to_update.append(calculate_phone_numbers_validity(individual))
    Individual.objects.bulk_update(
        individuals_to_update, fields=("phone_no_valid", "phone_no_alternative_valid"), batch_size=1000
    )


@app.task()
@log_start_and_end
@sentry_tags
def enroll_households_to_program_task(households_ids: List, program_for_enroll_id: str, user_id: str) -> None:
    task_params = {
        "task_name": "enroll_households_to_program_task",
        "household_ids": sorted([str(household_id) for household_id in households_ids]),
        "program_for_enroll_id": program_for_enroll_id,
    }
    task_params_str = json.dumps(task_params, sort_keys=True)
    cache_key = hashlib.sha256(task_params_str.encode()).hexdigest()
    if cache.get(cache_key):
        logger.info("Task enroll_households_to_program_task with this data is already running.")
        return

    # 1 day timeout
    cache.set(cache_key, True, timeout=24 * 60 * 60)
    try:
        households = Household.objects.filter(pk__in=households_ids)
        program_for_enroll = Program.objects.get(id=program_for_enroll_id)
        enroll_households_to_program(households, program_for_enroll, user_id)
        populate_index(
            Individual.objects.filter(program=program_for_enroll),
            get_individual_doc(program_for_enroll.business_area.slug),
        )
        populate_index(Household.objects.filter(program=program_for_enroll), HouseholdDocument)
    finally:
        cache.delete(cache_key)


@app.task()
@log_start_and_end
@sentry_tags
def mass_withdraw_households_from_list_task(household_id_list: list, tag: str, program_id: str) -> None:
    from hct_mis_api.apps.household.admin.household import (
        HouseholdWithdrawFromListMixin,
    )

    program = Program.objects.get(id=program_id)
    HouseholdWithdrawFromListMixin().mass_withdraw_households_from_list_bulk(household_id_list, tag, program)
