from datetime import timedelta
from unittest.mock import Mock, patch
import uuid

from django.utils import timezone
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.core.utils import stable_ids_hash
from hope.apps.household.celery_tasks import (
    calculate_children_fields_for_not_collected_individual_data_async_task,
    calculate_children_fields_for_not_collected_individual_data_async_task_action,
    cleanup_indexes_in_inactive_programs_async_task,
    cleanup_indexes_in_inactive_programs_async_task_action,
    enroll_households_to_program_async_task,
    enroll_households_to_program_async_task_action,
    interval_recalculate_population_fields_async_task,
    interval_recalculate_population_fields_async_task_action,
    mass_withdraw_households_from_list_async_task,
    mass_withdraw_households_from_list_async_task_action,
    recalculate_population_fields_async_task,
    recalculate_population_fields_async_task_action,
    recalculate_population_fields_chunk_async_task,
    recalculate_population_fields_chunk_async_task_action,
    revalidate_phone_number_async_task,
    revalidate_phone_number_async_task_action,
)
from hope.apps.household.const import ROLE_PRIMARY
from hope.models import AsyncJob, Document, Household, IndividualIdentity, Program
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


def create_async_job(action: str, config: dict, program: Program | None = None) -> AsyncJob:
    return AsyncJob.objects.create(
        type="JOB_TASK",
        action=action,
        config=config,
        program=program,
    )


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program_source(business_area):
    return ProgramFactory(status=Program.ACTIVE, name="Program source", business_area=business_area)


@pytest.fixture
def program_target(business_area):
    return ProgramFactory(status=Program.ACTIVE, name="Program target", business_area=business_area)


@pytest.fixture
def household_one_context(business_area, program_source):
    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program_source,
    )
    household = HouseholdFactory(
        business_area=business_area,
        program=program_source,
        head_of_household=individual,
        create_role=False,
    )
    household.head_of_household = individual
    household.household_collection = None
    household.save(update_fields=["head_of_household", "household_collection"])
    individual.individual_collection = None
    individual.save(update_fields=["individual_collection"])
    IndividualRoleInHouseholdFactory(
        individual=individual,
        household=household,
        role=ROLE_PRIMARY,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    DocumentFactory(individual=individual, program=individual.program, rdi_merge_status=MergeStatusModel.MERGED)
    IndividualIdentityFactory(individual=individual, rdi_merge_status=MergeStatusModel.MERGED)
    return {"household": household, "individual": individual}


@pytest.fixture
def household_two_context(business_area, program_source, program_target):
    household_source = HouseholdFactory(
        business_area=business_area,
        program=program_source,
    )
    individual_source = household_source.individuals.first()
    if household_source.household_collection is None:
        household_source.household_collection = HouseholdCollectionFactory()
        household_source.save(update_fields=["household_collection"])
    if individual_source.individual_collection is None:
        individual_source.individual_collection = IndividualCollectionFactory()
        individual_source.save(update_fields=["individual_collection"])

    individual_target = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program_target,
        individual_collection=individual_source.individual_collection,
    )
    individual_target.unicef_id = individual_source.unicef_id
    individual_target.save(update_fields=["unicef_id"])
    household_target = HouseholdFactory(
        business_area=business_area,
        program=program_target,
        household_collection=household_source.household_collection,
        head_of_household=individual_target,
        create_role=False,
    )
    household_target.unicef_id = household_source.unicef_id
    household_target.save(update_fields=["unicef_id"])

    return {
        "household_source": household_source,
        "individual_source": individual_source,
        "household_target": household_target,
        "individual_target": individual_target,
    }


@pytest.mark.elasticsearch
def test_enroll_households_to_program_task(
    user,
    program_source,
    program_target,
    household_one_context,
    household_two_context,
) -> None:
    household1 = household_one_context["household"]
    individual = household_one_context["individual"]
    household2 = household_two_context["household_source"]

    assert program_target.households.count() == 1
    assert program_target.individuals.count() == 1
    assert program_source.households.count() == 2
    assert program_source.individuals.count() == 2

    assert household1.household_collection is None

    assert Household.objects.filter(unicef_id=household1.unicef_id).count() == 1
    assert Household.objects.filter(unicef_id=household2.unicef_id).count() == 2

    job = create_async_job(
        "hope.apps.household.celery_tasks.enroll_households_to_program_async_task_action",
        {
            "households_ids": [str(household1.id), str(household2.id)],
            "program_for_enroll_id": str(program_target.id),
            "user_id": str(user.pk),
        },
        program_target,
    )
    enroll_households_to_program_async_task_action(job)
    household1.refresh_from_db()
    household2.refresh_from_db()

    assert program_target.households.count() == 2
    assert program_target.individuals.count() == 2
    assert program_source.households.count() == 2
    assert program_source.individuals.count() == 2

    assert household1.household_collection is not None

    assert Household.objects.filter(unicef_id=household1.unicef_id).count() == 2
    assert Household.objects.filter(unicef_id=household2.unicef_id).count() == 2
    enrolled_household = Household.objects.filter(program=program_target, unicef_id=household1.unicef_id).first()
    assert (
        enrolled_household.individuals_and_roles.filter(role=ROLE_PRIMARY).first().individual.unicef_id
        == individual.unicef_id
    )
    assert Document.objects.filter(individual__household=enrolled_household).count() == 1
    assert IndividualIdentity.objects.filter(individual__household=enrolled_household).count() == 1


@pytest.mark.parametrize(
    ("days_ago", "should_delete"),
    [
        (7, True),  # same date - 7 days ago, matches
        (6.9, True),  # same date, matches
        (7.5, False),  # day before, no match
        (8, False),  # day before, no match
        (6, False),  # too recent, no match
        (0, False),  # just now, no match
    ],
)
@freeze_time("2026-02-26 01:00:00")
@patch("hope.apps.household.celery_tasks.delete_program_indexes", return_value=(True, "ok"))
def test_cleanup_inactive_program_indexes_task_window(delete_mock, days_ago, should_delete):
    program = ProgramFactory(status=Program.FINISHED)
    updated_at = timezone.now() - timedelta(days=days_ago)
    Program.objects.filter(pk=program.pk).update(updated_at=updated_at)

    job = create_async_job(
        "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task_action", {}
    )
    cleanup_indexes_in_inactive_programs_async_task_action(job)

    if should_delete:
        delete_mock.assert_called_once_with(str(program.id))
    else:
        delete_mock.assert_not_called()


@freeze_time("2026-02-26 01:00:00")
@patch("hope.apps.household.celery_tasks.delete_program_indexes", return_value=(True, "ok"))
def test_cleanup_inactive_program_indexes_task_skips_active(delete_mock):
    program = ProgramFactory(status=Program.ACTIVE)
    Program.objects.filter(pk=program.pk).update(updated_at=timezone.now() - timedelta(days=7))

    job = create_async_job(
        "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task_action", {}
    )
    cleanup_indexes_in_inactive_programs_async_task_action(job)

    delete_mock.assert_not_called()


@freeze_time("2026-02-26 01:00:00")
@patch("hope.apps.household.celery_tasks.delete_program_indexes", return_value=(True, "ok"))
def test_cleanup_inactive_program_indexes_task_multiple_programs(delete_mock):
    to_cleanup = ProgramFactory(status=Program.FINISHED)
    too_recent = ProgramFactory(status=Program.FINISHED)
    too_old = ProgramFactory(status=Program.FINISHED)
    active = ProgramFactory(status=Program.ACTIVE)

    Program.objects.filter(pk=to_cleanup.pk).update(updated_at=timezone.now() - timedelta(days=7))
    Program.objects.filter(pk=too_recent.pk).update(updated_at=timezone.now() - timedelta(days=3))
    Program.objects.filter(pk=too_old.pk).update(updated_at=timezone.now() - timedelta(days=10))
    Program.objects.filter(pk=active.pk).update(updated_at=timezone.now() - timedelta(days=7))

    job = create_async_job(
        "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task_action", {}
    )
    cleanup_indexes_in_inactive_programs_async_task_action(job)

    delete_mock.assert_called_once_with(str(to_cleanup.id))


@patch.object(AsyncJob, "queue")
def test_enroll_households_to_program_task_schedules_async_job(mock_queue, user, program_target):
    hh_id = uuid.uuid4()
    enroll_households_to_program_async_task(
        households_ids=[hh_id],
        program_for_enroll_id=str(program_target.id),
        user_id=str(user.pk),
    )

    job = AsyncJob.objects.get()

    assert job.owner == user
    assert job.program == program_target
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.household.celery_tasks.enroll_households_to_program_async_task_action"
    assert job.config == {
        "households_ids": [str(hh_id)],
        "program_for_enroll_id": str(program_target.id),
        "user_id": str(user.pk),
    }
    assert (
        job.group_key == f"enroll_households_to_program_async_task:{program_target.id}:{stable_ids_hash([str(hh_id)])}"
    )
    assert job.description == f"Enroll households to program {program_target.id}"
    mock_queue.assert_called_once_with()


@patch.object(AsyncJob, "queue")
def test_cleanup_inactive_program_indexes_task_schedules_async_job(mock_queue):
    cleanup_indexes_in_inactive_programs_async_task()

    job = AsyncJob.objects.get()

    assert job.owner is None
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task_action"
    assert job.config == {}
    assert job.group_key == "cleanup_indexes_in_inactive_programs_async_task"
    assert job.description == "Cleanup indexes in inactive programs"
    mock_queue.assert_called_once_with()


@patch.object(AsyncJob, "queue")
def test_recalculate_population_fields_chunk_task_schedules_async_job(mock_queue):
    recalculate_population_fields_chunk_async_task(households_ids=["hh-1"], program_id=None)

    job = AsyncJob.objects.get()

    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.household.celery_tasks.recalculate_population_fields_chunk_async_task_action"
    assert job.config == {"households_ids": ["hh-1"], "program_id": None}
    assert job.group_key == f"recalculate_population_fields_chunk_async_task:None:{stable_ids_hash(['hh-1'])}"
    assert job.description == "Recalculate population fields chunk"
    mock_queue.assert_called_once_with()


@patch.object(AsyncJob, "queue")
def test_recalculate_population_fields_task_schedules_async_job(mock_queue):
    recalculate_population_fields_async_task(household_ids=["hh-1"], program_id=None)

    job = AsyncJob.objects.get()

    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.household.celery_tasks.recalculate_population_fields_async_task_action"
    assert job.config == {"household_ids": ["hh-1"], "program_id": None}
    assert job.group_key == f"recalculate_population_fields_async_task:None:{stable_ids_hash(['hh-1'])}"
    assert job.description == "Schedule population fields recalculation"
    mock_queue.assert_called_once_with()


@patch.object(AsyncJob, "queue")
def test_interval_recalculate_population_fields_task_schedules_async_job(mock_queue):
    interval_recalculate_population_fields_async_task()

    job = AsyncJob.objects.get()

    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.household.celery_tasks.interval_recalculate_population_fields_async_task_action"
    assert job.config == {}
    assert job.group_key == "interval_recalculate_population_fields_async_task"
    assert job.description == "Run interval population fields recalculation"
    mock_queue.assert_called_once_with()


@patch.object(AsyncJob, "queue")
def test_revalidate_phone_number_task_schedules_async_job(mock_queue):
    individual_id = uuid.uuid4()
    revalidate_phone_number_async_task(individual_ids=[individual_id])

    job = AsyncJob.objects.get()

    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.household.celery_tasks.revalidate_phone_number_async_task_action"
    assert job.config == {"individual_ids": [str(individual_id)]}
    assert job.group_key == f"revalidate_phone_number_async_task:{stable_ids_hash([str(individual_id)])}"
    assert job.description == "Revalidate phone numbers for individuals"
    mock_queue.assert_called_once_with()


@patch("hope.apps.household.celery_tasks.calculate_phone_numbers_validity")
def test_revalidate_phone_number_task_action_updates_individuals(
    mock_calculate_phone_numbers_validity, business_area, program_source
):
    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program_source,
    )
    mock_calculate_phone_numbers_validity.side_effect = lambda ind: ind
    job = create_async_job(
        "hope.apps.household.celery_tasks.revalidate_phone_number_async_task_action",
        {"individual_ids": [str(individual.id)]},
    )
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])

    revalidate_phone_number_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "previous failure"}
    mock_calculate_phone_numbers_validity.assert_called_once()


@patch("hope.apps.household.celery_tasks.calculate_phone_numbers_validity", side_effect=RuntimeError("phone failed"))
def test_revalidate_phone_number_task_action_sets_job_errors_on_failure(
    mock_calculate_phone_numbers_validity, business_area, program_source
):
    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program_source,
    )
    job = create_async_job(
        "hope.apps.household.celery_tasks.revalidate_phone_number_async_task_action",
        {"individual_ids": [str(individual.id)]},
    )

    with pytest.raises(RuntimeError, match="phone failed"):
        revalidate_phone_number_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "phone failed"}
    mock_calculate_phone_numbers_validity.assert_called_once()


@patch.object(AsyncJob, "queue")
def test_mass_withdraw_households_from_list_task_schedules_async_job(mock_queue, program_source):
    mass_withdraw_households_from_list_async_task(
        household_id_list=["hh-1"], tag="tag-1", program_id=str(program_source.id)
    )

    job = AsyncJob.objects.get()

    assert job.program == program_source
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.household.celery_tasks.mass_withdraw_households_from_list_async_task_action"
    assert job.config == {"household_id_list": ["hh-1"], "tag": "tag-1", "program_id": str(program_source.id)}
    assert (
        job.group_key
        == f"mass_withdraw_households_from_list_async_task:{program_source.id}:tag-1:{stable_ids_hash(['hh-1'])}"
    )
    assert job.description == f"Mass withdraw households from list for program {program_source.id}"
    mock_queue.assert_called_once_with()


@patch("hope.apps.household.celery_tasks.Program.objects.get")
@patch("hope.admin.household.HouseholdWithdrawFromListMixin")
def test_mass_withdraw_households_from_list_task_action_success(mock_withdraw_mixin, mock_program_get, program_source):
    mock_program_get.return_value = program_source
    job = create_async_job(
        "hope.apps.household.celery_tasks.mass_withdraw_households_from_list_async_task_action",
        {"household_id_list": ["hh-1"], "tag": "tag-1", "program_id": str(program_source.id)},
        program_source,
    )
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])

    mass_withdraw_households_from_list_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "previous failure"}
    mock_withdraw_mixin.return_value.mass_withdraw_households_from_list_bulk.assert_called_once_with(
        ["hh-1"], "tag-1", program_source
    )


@patch("hope.apps.household.celery_tasks.Program.objects.get", side_effect=RuntimeError("withdraw failed"))
def test_mass_withdraw_households_from_list_task_action_sets_job_errors_on_failure(mock_program_get, program_source):
    job = create_async_job(
        "hope.apps.household.celery_tasks.mass_withdraw_households_from_list_async_task_action",
        {"household_id_list": ["hh-1"], "tag": "tag-1", "program_id": str(program_source.id)},
        program_source,
    )

    with pytest.raises(RuntimeError, match="withdraw failed"):
        mass_withdraw_households_from_list_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "withdraw failed"}
    mock_program_get.assert_called_once_with(id=str(program_source.id))


@patch.object(AsyncJob, "queue")
def test_calculate_children_fields_for_not_collected_individual_data_schedules_async_job(mock_queue):
    calculate_children_fields_for_not_collected_individual_data_async_task()

    job = AsyncJob.objects.get()

    assert job.type == "JOB_TASK"
    assert (
        job.action == "hope.apps.household.celery_tasks."
        "calculate_children_fields_for_not_collected_individual_data_async_task_action"
    )
    assert job.config == {}
    assert job.group_key == "calculate_children_fields_for_not_collected_individual_data_async_task"
    assert job.description == "Calculate children fields for households"
    mock_queue.assert_called_once_with()


def test_calculate_children_fields_for_not_collected_individual_data_action_preserves_existing_errors():
    job = create_async_job(
        "hope.apps.household.celery_tasks.calculate_children_fields_for_not_collected_individual_data_async_task_action",
        {},
    )
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])

    calculate_children_fields_for_not_collected_individual_data_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "previous failure"}


@patch("hope.apps.household.celery_tasks.recalculate_data", side_effect=RuntimeError("chunk failed"))
def test_recalculate_population_fields_chunk_task_action_sets_job_errors_on_failure(
    mock_recalculate_data, business_area, program_source
):
    household = HouseholdFactory(business_area=business_area, program=program_source)
    job = create_async_job(
        "hope.apps.household.celery_tasks.recalculate_population_fields_chunk_async_task_action",
        {"households_ids": [str(household.id)], "program_id": None},
        program_source,
    )

    with pytest.raises(RuntimeError, match="chunk failed"):
        recalculate_population_fields_chunk_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "chunk failed"}
    mock_recalculate_data.assert_called_once()


@patch("hope.apps.household.celery_tasks.recalculate_population_fields_chunk_async_task")
def test_recalculate_population_fields_task_action_skips_when_recalculation_disabled(mock_chunk_delay, business_area):
    program = ProgramFactory(business_area=business_area)
    data_collecting_type = program.data_collecting_type
    data_collecting_type.recalculate_composition = False
    data_collecting_type.save(update_fields=["recalculate_composition"])
    household = HouseholdFactory(business_area=business_area, program=program)
    job = create_async_job(
        "hope.apps.household.celery_tasks.recalculate_population_fields_async_task_action",
        {"household_ids": [str(household.id)], "program_id": str(program.id)},
        program,
    )

    recalculate_population_fields_async_task_action(job)

    mock_chunk_delay.assert_not_called()


@patch("hope.apps.household.celery_tasks.Program.objects.get", side_effect=RuntimeError("schedule failed"))
def test_recalculate_population_fields_task_action_sets_job_errors_on_failure(mock_program_get):
    job = create_async_job(
        "hope.apps.household.celery_tasks.recalculate_population_fields_async_task_action",
        {"household_ids": ["hh-1"], "program_id": "program-1"},
    )

    with pytest.raises(RuntimeError, match="schedule failed"):
        recalculate_population_fields_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "schedule failed"}
    mock_program_get.assert_called_once_with(id="program-1")


@patch(
    "hope.apps.household.celery_tasks.recalculate_population_fields_async_task",
    side_effect=RuntimeError("interval failed"),
)
def test_interval_recalculate_population_fields_task_action_sets_job_errors_on_failure(mock_recalculate_task):
    job = create_async_job(
        "hope.apps.household.celery_tasks.interval_recalculate_population_fields_async_task_action",
        {},
    )

    with pytest.raises(RuntimeError, match="interval failed"):
        interval_recalculate_population_fields_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "interval failed"}
    mock_recalculate_task.assert_called_once()


@patch("hope.apps.household.celery_tasks.recalculate_population_fields_async_task")
@patch("hope.models.Individual.objects.filter")
def test_interval_recalculate_population_fields_task_action_collects_household_ids(
    mock_filter: Mock, mock_recalculate_task: Mock
) -> None:
    queryset = Mock()
    queryset.order_by.return_value = queryset
    queryset.values_list.return_value = queryset
    queryset.distinct.return_value = list(range(10))
    mock_filter.return_value = queryset
    job = create_async_job(
        "hope.apps.household.celery_tasks.interval_recalculate_population_fields_async_task_action",
        {},
    )

    interval_recalculate_population_fields_async_task_action(job)

    mock_recalculate_task.assert_called_once_with(household_ids=[str(i) for i in range(10)])


@patch("hope.models.Household.objects.filter")
def test_calculate_children_fields_for_not_collected_individual_data_action_sets_job_errors_on_failure(mock_filter):
    job = create_async_job(
        "hope.apps.household.celery_tasks.calculate_children_fields_for_not_collected_individual_data_async_task_action",
        {},
    )
    mock_filter.return_value.update.side_effect = RuntimeError("children failed")

    with pytest.raises(RuntimeError, match="children failed"):
        calculate_children_fields_for_not_collected_individual_data_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "children failed"}


@patch("hope.apps.household.celery_tasks.cache.get", return_value=True)
@patch("hope.apps.household.celery_tasks.enroll_households_to_program_async_task")
def test_enroll_households_to_program_task_action_returns_early_when_already_running(
    mock_enroll, mock_cache_get, program_source
):
    job = create_async_job(
        "hope.apps.household.celery_tasks.enroll_households_to_program_async_task_action",
        {
            "households_ids": ["hh-1"],
            "program_for_enroll_id": str(program_source.id),
            "user_id": "user-1",
        },
        program_source,
    )

    enroll_households_to_program_async_task_action(job)

    mock_cache_get.assert_called_once()
    mock_enroll.assert_not_called()


@patch("hope.apps.household.celery_tasks.cache.delete")
@patch(
    "hope.apps.household.celery_tasks.enroll_households_to_program_async_task",
    side_effect=RuntimeError("enroll failed"),
)
@patch("hope.apps.household.celery_tasks.Program.objects.get")
def test_enroll_households_to_program_task_action_sets_job_errors_on_failure(
    mock_program_get, mock_enroll, mock_cache_delete, program_source
):
    mock_program_get.return_value = program_source
    household = HouseholdFactory(business_area=program_source.business_area, program=program_source)
    job = create_async_job(
        "hope.apps.household.celery_tasks.enroll_households_to_program_async_task_action",
        {
            "households_ids": [str(household.id)],
            "program_for_enroll_id": str(program_source.id),
            "user_id": "user-1",
        },
        program_source,
    )

    with pytest.raises(RuntimeError, match="enroll failed"):
        enroll_households_to_program_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "enroll failed"}
    mock_cache_delete.assert_called_once()


@patch("hope.apps.household.celery_tasks.delete_program_indexes", side_effect=RuntimeError("cleanup failed"))
def test_cleanup_indexes_in_inactive_programs_task_action_sets_job_errors_on_failure(mock_delete):
    program = ProgramFactory(status=Program.FINISHED)
    Program.objects.filter(pk=program.pk).update(updated_at=timezone.now() - timedelta(days=7))
    job = create_async_job(
        "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task_action", {}
    )

    with pytest.raises(RuntimeError, match="cleanup failed"):
        cleanup_indexes_in_inactive_programs_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "cleanup failed"}
    mock_delete.assert_called_once_with(str(program.id))
