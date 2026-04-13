from datetime import timedelta
import hashlib
import json
import logging
from uuid import UUID

from concurrency.api import disable_concurrency
from constance import config
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from hope.apps.core.celery import app
from hope.apps.core.utils import stable_ids_hash
from hope.apps.household.documents import (
    get_household_doc,
    get_individual_doc,
)
from hope.apps.household.services.household_recalculate_data import recalculate_data
from hope.apps.household.services.index_management import delete_program_indexes
from hope.apps.program.utils import enroll_households_to_program
from hope.apps.utils.elasticsearch_utils import populate_index
from hope.apps.utils.phone import calculate_phone_numbers_validity
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncJob, Household, Individual, Program

logger = logging.getLogger(__name__)


def recalculate_population_fields_chunk_async_task_action(job: AsyncJob) -> None:
    from hope.models import Household, Individual

    households_ids = job.config["households_ids"]
    program_id = job.config["program_id"]

    # memory optimization
    paginator = Paginator(households_ids, 200)

    with disable_concurrency(Household), disable_concurrency(Individual):
        program = Program.objects.get(id=program_id) if program_id else None
        with transaction.atomic():
            for page in paginator.page_range:
                logger.info(
                    f"recalculate_population_fields_chunk_async_task: Processing page {page} of {paginator.num_pages}"
                )
                households_ids_page = paginator.page(page).object_list
                households_to_update = []
                fields_to_update = []
                for hh in (
                    Household.objects.filter(pk__in=households_ids_page)
                    .select_related("business_area")
                    .only("id", "business_area_id", "business_area__name")
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


def recalculate_population_fields_chunk_async_task(households_ids: list[str], program_id: str | None) -> None:
    AsyncJob.queue_task(
        job_name=recalculate_population_fields_chunk_async_task.__name__,
        program_id=program_id,
        action="hope.apps.household.celery_tasks.recalculate_population_fields_chunk_async_task_action",
        config={"households_ids": households_ids, "program_id": program_id},
        group_key=f"recalculate_population_fields_chunk_async_task:{program_id}:{stable_ids_hash(households_ids)}",
        description="Recalculate population fields chunk",
    )


def recalculate_population_fields_async_task_action(job: AsyncJob) -> None:
    from hope.models import Household

    household_ids = job.config["household_ids"]
    program_id = job.config["program_id"]

    params = {}
    if household_ids:
        params["pk__in"] = household_ids
    recalculate_composition = None
    if program_id:
        program = Program.objects.get(id=program_id)
        recalculate_composition = program.data_collecting_type.recalculate_composition
    queryset = Household.objects.filter(**params).only("pk").order_by("pk")
    if not recalculate_composition:
        queryset = queryset.none()

    if queryset.exists():
        paginator = Paginator(queryset, config.RECALCULATE_POPULATION_FIELDS_CHUNK)

        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            recalculate_population_fields_chunk_async_task(
                households_ids=[str(_id) for _id in page.object_list.values_list("pk", flat=True)],
                program_id=program_id,
            )


def recalculate_population_fields_async_task(household_ids: list[str], program_id: str | None = None) -> None:
    serialized_household_ids = [str(household_id) for household_id in household_ids]
    AsyncJob.queue_task(
        job_name=recalculate_population_fields_async_task.__name__,
        program_id=program_id,
        action="hope.apps.household.celery_tasks.recalculate_population_fields_async_task_action",
        config={
            "household_ids": serialized_household_ids,
            "program_id": program_id,
        },
        group_key=(
            f"recalculate_population_fields_async_task:{program_id}:{stable_ids_hash(serialized_household_ids)}"
        ),
        description="Schedule population fields recalculation",
    )


def interval_recalculate_population_fields_async_task_action(job: AsyncJob) -> None:
    from hope.models import Individual

    datetime_now = timezone.now()
    now_day, now_month = datetime_now.day, datetime_now.month

    households = (
        Individual.objects.filter(birth_date__day=now_day, birth_date__month=now_month)
        .order_by("household_id")
        .values_list("household_id", flat=True)
        .distinct("household_id")
    )

    recalculate_population_fields_async_task(household_ids=[str(_id) for _id in households])


@app.task()
def interval_recalculate_population_fields_async_task() -> None:
    AsyncJob.queue_task(
        job_name=interval_recalculate_population_fields_async_task.__name__,
        action="hope.apps.household.celery_tasks.interval_recalculate_population_fields_async_task_action",
        group_key="interval_recalculate_population_fields_async_task",
        description="Run interval population fields recalculation",
    )


def calculate_children_fields_for_not_collected_individual_data_async_task_action(job: AsyncJob) -> int:
    from django.db.models.functions import Coalesce

    from hope.models import Household  # pragma: no cover

    return Household.objects.filter(program__data_collecting_type__recalculate_composition=True).update(
        # TODO: count differently or add all the fields for the new gender options
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


def calculate_children_fields_for_not_collected_individual_data_async_task() -> None:
    AsyncJob.queue_task(
        job_name=calculate_children_fields_for_not_collected_individual_data_async_task.__name__,
        action="hope.apps.household.celery_tasks.calculate_children_fields_for_not_collected_individual_data_async_task_action",
        config={},
        group_key="calculate_children_fields_for_not_collected_individual_data_async_task",
        description="Calculate children fields for households",
    )


def revalidate_phone_number_async_task_action(job: AsyncJob) -> None:
    individual_ids = job.config["individual_ids"]
    individuals = Individual.objects.filter(pk__in=individual_ids).only("phone_no", "phone_no_alternative")
    individuals_to_update = [calculate_phone_numbers_validity(individual) for individual in individuals]
    Individual.objects.bulk_update(
        individuals_to_update,
        fields=("phone_no_valid", "phone_no_alternative_valid"),
        batch_size=1000,
    )


def revalidate_phone_number_async_task(individual_ids: list[UUID]) -> None:
    serialized_individual_ids = [str(individual_id) for individual_id in individual_ids]
    AsyncJob.queue_task(
        job_name=revalidate_phone_number_async_task.__name__,
        action="hope.apps.household.celery_tasks.revalidate_phone_number_async_task_action",
        config={"individual_ids": serialized_individual_ids},
        group_key=f"revalidate_phone_number_async_task:{stable_ids_hash(serialized_individual_ids)}",
        description="Revalidate phone numbers for individuals",
    )


def enroll_households_to_program_async_task_action(job: AsyncJob) -> None:
    households_ids = job.config["households_ids"]
    program_for_enroll_id = job.config["program_for_enroll_id"]
    user_id = job.config["user_id"]
    task_params = {
        "task_name": "enroll_households_to_program_async_task",
        "household_ids": sorted([str(household_id) for household_id in households_ids]),
        "program_for_enroll_id": program_for_enroll_id,
    }
    task_params_str = json.dumps(task_params, sort_keys=True)
    cache_key = hashlib.sha256(task_params_str.encode()).hexdigest()
    if cache.get(cache_key):
        logger.info("Task enroll_households_to_program_async_task with this data is already running.")
        return

    # 1 day timeout
    cache.set(cache_key, True, timeout=24 * 60 * 60)
    try:
        households = Household.objects.filter(pk__in=households_ids)
        program_for_enroll = Program.objects.get(id=program_for_enroll_id)
        enroll_households_to_program(households, program_for_enroll, user_id)
        if program_for_enroll.status == Program.ACTIVE:
            populate_index(
                Individual.objects.filter(household__copied_from_id__in=households_ids, program=program_for_enroll),
                get_individual_doc(str(program_for_enroll.id)),
            )
            populate_index(
                Household.objects.filter(copied_from_id__in=households_ids, program=program_for_enroll),
                get_household_doc(str(program_for_enroll.id)),
            )
    finally:
        cache.delete(cache_key)


def enroll_households_to_program_async_task(
    households_ids: list[UUID],
    program_for_enroll_id: str,
    user_id: str,
) -> None:
    households_ids = [str(_id) for _id in households_ids]
    AsyncJob.queue_task(
        job_name=enroll_households_to_program_async_task.__name__,
        owner_id=user_id,
        program_id=program_for_enroll_id,
        action="hope.apps.household.celery_tasks.enroll_households_to_program_async_task_action",
        config={
            "households_ids": households_ids,
            "program_for_enroll_id": program_for_enroll_id,
            "user_id": user_id,
        },
        group_key=f"enroll_households_to_program_async_task:{program_for_enroll_id}:{stable_ids_hash(households_ids)}",
        description=f"Enroll households to program {program_for_enroll_id}",
    )


def mass_withdraw_households_from_list_async_task_action(job: AsyncJob) -> None:
    from hope.admin.household import HouseholdWithdrawFromListMixin

    household_id_list = job.config["household_id_list"]
    tag = job.config["tag"]
    program_id = job.config["program_id"]
    program = Program.objects.get(id=program_id)
    HouseholdWithdrawFromListMixin().mass_withdraw_households_from_list_bulk(household_id_list, tag, program)


def mass_withdraw_households_from_list_async_task(
    household_id_list: list[str],
    tag: str,
    program_id: Program | str,
) -> None:
    serialized_program_id = str(program_id.id) if isinstance(program_id, Program) else str(program_id)
    AsyncJob.queue_task(
        job_name=mass_withdraw_households_from_list_async_task.__name__,
        program_id=serialized_program_id,
        action="hope.apps.household.celery_tasks.mass_withdraw_households_from_list_async_task_action",
        config={"household_id_list": household_id_list, "tag": tag, "program_id": serialized_program_id},
        group_key=(
            f"mass_withdraw_households_from_list_async_task:{serialized_program_id}:{tag}:{stable_ids_hash(household_id_list)}"
        ),
        description=f"Mass withdraw households from list for program {serialized_program_id}",
    )


def cleanup_indexes_in_inactive_programs_async_task_action(job: AsyncJob) -> None:
    cutoff = timezone.now() - timedelta(days=7)

    inactive_programs = Program.objects.filter(
        status__in=[Program.FINISHED, Program.DRAFT],
        updated_at__date=cutoff.date(),
    )

    for program in inactive_programs:
        delete_program_indexes(str(program.id))


@app.task()
def cleanup_indexes_in_inactive_programs_async_task() -> None:
    AsyncJob.queue_task(
        job_name=cleanup_indexes_in_inactive_programs_async_task.__name__,
        action="hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task_action",
        config={},
        group_key="cleanup_indexes_in_inactive_programs_async_task",
        description="Cleanup indexes in inactive programs",
    )
