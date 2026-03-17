from datetime import timedelta
from typing import Any
from unittest.mock import Mock, patch

from django.db import Error
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    IndividualFactory,
    ProgramFactory,
    SanctionListFactory,
)
from hope.apps.grievance.celery_tasks import (
    deduplicate_and_check_against_sanctions_list_task_single_individual_action,
    periodic_grievances_notifications,
    periodic_grievances_notifications_action,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.tasks.deduplicate_and_check_sanctions import (
    deduplicate_and_check_against_sanctions_list_task_single_individual,
)
from hope.models import AsyncJob

pytestmark = pytest.mark.django_db


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
    mock_queue: Mock, task_context: dict[str, Any]
) -> None:
    individual = task_context["individual"]

    from hope.apps.grievance.celery_tasks import deduplicate_and_check_against_sanctions_list_task_single_individual

    deduplicate_and_check_against_sanctions_list_task_single_individual(True, str(individual.id))

    job = AsyncJob.objects.get()

    assert job.owner is None
    assert job.type == "JOB_TASK"
    assert (
        job.action
        == "hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_action"
    )
    assert job.config == {"should_populate_index": True, "individual_id": str(individual.id)}
    assert job.group_key == f"grievance_single_individual_deduplication:{individual.id}"
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
        "hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_action",
        {"should_populate_index": True, "individual_id": str(individual.id)},
    )
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])

    deduplicate_and_check_against_sanctions_list_task_single_individual_action(job)

    job.refresh_from_db()
    assert job.errors == {}
    mock_task.assert_called_once_with(True, individual)
    mock_set_sentry_tag.assert_called_once_with(individual.business_area.name)


@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.deduplicate_and_check_against_sanctions_list_task_single_individual",
    side_effect=Error("db failed"),
)
def test_deduplicate_and_check_sanctions_single_individual_action_sets_job_errors(
    mock_task: Mock, task_context: dict[str, Any]
) -> None:
    individual = task_context["individual"]
    job = create_async_job(
        "hope.apps.grievance.celery_tasks.deduplicate_and_check_against_sanctions_list_task_single_individual_action",
        {"should_populate_index": True, "individual_id": str(individual.id)},
    )

    with pytest.raises(Error, match="db failed"):
        deduplicate_and_check_against_sanctions_list_task_single_individual_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "db failed"}


@patch.object(AsyncJob, "queue")
def test_periodic_grievances_notifications_schedules_async_job(mock_queue: Mock) -> None:
    periodic_grievances_notifications()

    job = AsyncJob.objects.get()

    assert job.owner is None
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.grievance.celery_tasks.periodic_grievances_notifications_action"
    assert job.config == {}
    assert job.group_key == "periodic_grievances_notifications"
    assert job.description == "Send periodic grievance notifications"
    mock_queue.assert_called_once_with()


@patch("hope.apps.grievance.celery_tasks.GrievanceNotification")
def test_periodic_grievances_notifications_action_sends_notifications(mock_notification_cls: Mock) -> None:
    business_area = BusinessAreaFactory(enable_email_notification=True)
    sensitive_ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        status=GrievanceTicket.STATUS_NEW,
        last_notification_sent=None,
    )
    sensitive_ticket.created_at = timezone.now() - timedelta(days=2)
    sensitive_ticket.save(update_fields=["created_at"])
    other_ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        status=GrievanceTicket.STATUS_NEW,
        last_notification_sent=None,
    )
    other_ticket.created_at = timezone.now() - timedelta(days=31)
    other_ticket.save(update_fields=["created_at"])
    job = create_async_job("hope.apps.grievance.celery_tasks.periodic_grievances_notifications_action", {})
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])

    periodic_grievances_notifications_action(job)

    sensitive_ticket.refresh_from_db()
    other_ticket.refresh_from_db()
    job.refresh_from_db()
    assert mock_notification_cls.call_count == 2
    assert sensitive_ticket.last_notification_sent is not None
    assert other_ticket.last_notification_sent is not None
    assert job.errors == {"error": "previous failure"}


@patch("hope.apps.grievance.celery_tasks.GrievanceNotification", side_effect=RuntimeError("send failed"))
def test_periodic_grievances_notifications_action_sets_job_errors_on_failure(mock_notification_cls: Mock) -> None:
    business_area = BusinessAreaFactory(enable_email_notification=True)
    sensitive_ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        status=GrievanceTicket.STATUS_NEW,
        last_notification_sent=None,
    )
    sensitive_ticket.created_at = timezone.now() - timedelta(days=2)
    sensitive_ticket.save(update_fields=["created_at"])
    job = create_async_job("hope.apps.grievance.celery_tasks.periodic_grievances_notifications_action", {})

    with pytest.raises(RuntimeError, match="send failed"):
        periodic_grievances_notifications_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "send failed"}
