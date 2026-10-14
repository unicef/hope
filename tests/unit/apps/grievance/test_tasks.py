from datetime import timedelta
from typing import Any
from unittest.mock import Mock, patch

from constance.forms import ConstanceForm
from django.core.exceptions import ValidationError
from django.db import Error
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    IndividualFactory,
    ProgramFactory,
    SanctionListFactory,
    UserFactory,
)
from hope.apps.grievance.celery_tasks import (
    deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.tasks.deduplicate_and_check_sanctions import (
    deduplicate_and_check_against_sanctions_list_task_single_individual,
)
from hope.models import AsyncJob

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("invalid_hour", [-1, 24])
def test_grievance_notification_hour_field_rejects_out_of_range_value(invalid_hour: int) -> None:
    notification_hour_field = ConstanceForm(initial={}).fields["GRIEVANCE_NOTIFICATION_HOUR"]

    with pytest.raises(ValidationError):
        notification_hour_field.clean(invalid_hour)


@pytest.fixture
def task_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    program = ProgramFactory(
        name="Test program ONE",
        business_area=business_area,
    )
    individual = IndividualFactory(
        household=None,
        program=program,
        business_area=business_area,
        full_name="Benjamin Butler",
        given_name="Benjamin",
        family_name="Butler",
        phone_no="(953)682-4596",
        birth_date="1943-07-30",
    )
    return {
        "business_area": business_area,
        "program": program,
        "individual": individual,
    }


def create_async_job(action: str, config: dict) -> AsyncJob:
    return AsyncJob.objects.create(
        type="JOB_TASK",
        action=action,
        config=config,
    )


@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.populate_index")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.HardDocumentDeduplication.deduplicate")
@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.DeduplicateTask.deduplicate_individuals_from_other_source"
)
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.create_needs_adjudication_tickets")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.check_against_sanction_list_pre_merge")
def test_execute_postponed_deduplication(
    sanction_execute_mock: Any,
    create_needs_adjudication_tickets_mock: Any,
    deduplicate_individuals_mock: Any,
    deduplicate_mock: Any,
    populate_index_mock: Any,
    task_context: dict[str, Any],
) -> None:
    business_area = task_context["business_area"]
    individual = task_context["individual"]
    business_area.postpone_deduplication = True
    business_area.save(update_fields=["postpone_deduplication"])

    deduplicate_and_check_against_sanctions_list_task_single_individual(
        should_populate_index=True,
        individual=individual,
    )

    assert populate_index_mock.call_count == 1
    assert deduplicate_mock.call_count == 1
    assert deduplicate_individuals_mock.call_count == 0
    assert create_needs_adjudication_tickets_mock.call_count == 0
    assert sanction_execute_mock.call_count == 0


@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.populate_index")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.HardDocumentDeduplication.deduplicate")
@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.DeduplicateTask.deduplicate_individuals_from_other_source"
)
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.create_needs_adjudication_tickets")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.check_against_sanction_list_pre_merge")
def test_execute_non_postponed_without_screening(
    sanction_execute_mock: Any,
    create_needs_adjudication_tickets_mock: Any,
    deduplicate_individuals_mock: Any,
    deduplicate_mock: Any,
    populate_index_mock: Any,
    task_context: dict[str, Any],
) -> None:
    business_area = task_context["business_area"]
    individual = task_context["individual"]
    business_area.postpone_deduplication = False
    business_area.save(update_fields=["postpone_deduplication"])

    deduplicate_and_check_against_sanctions_list_task_single_individual(
        should_populate_index=False,
        individual=individual,
    )

    assert populate_index_mock.call_count == 0
    assert deduplicate_mock.call_count == 1
    assert deduplicate_individuals_mock.call_count == 1
    assert create_needs_adjudication_tickets_mock.call_count == 2
    assert sanction_execute_mock.call_count == 0


@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.populate_index")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.HardDocumentDeduplication.deduplicate")
@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.DeduplicateTask.deduplicate_individuals_from_other_source"
)
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.create_needs_adjudication_tickets")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.check_against_sanction_list_pre_merge")
def test_execute_non_postponed_with_screening(
    sanction_execute_mock: Any,
    create_needs_adjudication_tickets_mock: Any,
    deduplicate_individuals_mock: Any,
    deduplicate_mock: Any,
    populate_index_mock: Any,
    task_context: dict[str, Any],
) -> None:
    business_area = task_context["business_area"]
    individual = task_context["individual"]
    program = task_context["program"]
    business_area.postpone_deduplication = False
    business_area.save(update_fields=["postpone_deduplication"])

    sanction_list = SanctionListFactory()
    program.sanction_lists.add(sanction_list)

    deduplicate_and_check_against_sanctions_list_task_single_individual(
        should_populate_index=False,
        individual=individual,
    )

    assert populate_index_mock.call_count == 0
    assert deduplicate_mock.call_count == 1
    assert deduplicate_individuals_mock.call_count == 1
    assert create_needs_adjudication_tickets_mock.call_count == 2
    assert sanction_execute_mock.call_count == 1


@patch.object(AsyncJob, "queue")
def test_deduplicate_and_check_sanctions_single_individual_task_schedules_async_job(
    mock_queue: Mock, task_context: dict[str, Any], django_capture_on_commit_callbacks
) -> None:
    individual = task_context["individual"]

    from hope.apps.grievance.celery_tasks import (
        deduplicate_and_check_against_sanctions_list_task_single_individual_async_task,
    )

    with django_capture_on_commit_callbacks(execute=True):
        deduplicate_and_check_against_sanctions_list_task_single_individual_async_task(True, individual)

    job = AsyncJob.objects.get()

    assert job.owner is None
    assert job.type == "JOB_TASK"
    assert (
        job.action == "hope.apps.grievance.celery_tasks."
        "deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action"
    )
    assert job.config == {"should_populate_index": True, "individual_id": str(individual.id)}
    assert job.group_key == "grievance"
    assert job.description == f"Deduplicate and sanctions-check grievance individual {individual.id}"
    mock_queue.assert_called_once_with()


@patch("hope.apps.grievance.celery_tasks.set_sentry_business_area_tag")
@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.deduplicate_and_check_against_sanctions_list_task_single_individual"
)
def test_deduplicate_and_check_sanctions_single_individual_action_success(
    mock_task: Mock, mock_set_sentry_tag: Mock, task_context: dict[str, Any]
) -> None:
    individual = task_context["individual"]
    job = create_async_job(
        "hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action",
        {"should_populate_index": True, "individual_id": str(individual.id)},
    )

    deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action(job)

    mock_task.assert_called_once_with(True, individual)
    mock_set_sentry_tag.assert_called_once_with(individual.business_area.name)


@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.deduplicate_and_check_against_sanctions_list_task_single_individual",
    side_effect=Error("db failed"),
)
def test_deduplicate_and_check_sanctions_single_individual_action_failure_reraises_error(
    mock_task: Mock, task_context: dict[str, Any]
) -> None:
    individual = task_context["individual"]
    job = create_async_job(
        "hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action",
        {"should_populate_index": True, "individual_id": str(individual.id)},
    )

    with pytest.raises(Error, match="db failed"):
        deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action(job)


def test_celery_task_returns_when_individual_not_found() -> None:
    job = create_async_job(
        "hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action",
        {"should_populate_index": False, "individual_id": "00000000-0000-0000-0000-000000000000"},
    )

    deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action(job)
    # No exception raised — task handles DoesNotExist gracefully


@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions"
    ".deduplicate_and_check_against_sanctions_list_task_single_individual"
)
def test_celery_task_calls_inner_function_with_individual(
    inner_fn_mock: Mock,
    task_context: dict[str, Any],
) -> None:
    individual = task_context["individual"]
    job = create_async_job(
        "hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action",
        {"should_populate_index": True, "individual_id": str(individual.pk)},
    )

    deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action(job)

    inner_fn_mock.assert_called_once()
    call_args = inner_fn_mock.call_args
    assert call_args[0][0] is True
    assert call_args[0][1].pk == individual.pk


def _make_ticket(
    category: int,
    status: int = GrievanceTicket.STATUS_NEW,
    enable_email: bool = True,
    created_days_ago: int = 2,
    last_notification_sent: Any = None,
) -> GrievanceTicket:
    business_area = BusinessAreaFactory(enable_email_notification=enable_email)
    # Map categories to valid issue types
    issue_type_map = {
        GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        GrievanceTicket.CATEGORY_DATA_CHANGE: GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    }
    issue_type = issue_type_map.get(category, GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=UserFactory(),
        category=category,
        issue_type=issue_type,
        status=status,
        last_notification_sent=last_notification_sent,
    )
    GrievanceTicket.objects.filter(pk=ticket.pk).update(
        created_at=timezone.now() - timedelta(days=created_days_ago),
    )
    return ticket
