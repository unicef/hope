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
    deduplicate_and_check_against_sanctions_list_task_single_individual_async_task_action,
    periodic_grievances_notifications_async_task,
    periodic_grievances_notifications_async_task_action,
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

    from hope.apps.grievance.celery_tasks import (
        deduplicate_and_check_against_sanctions_list_task_single_individual_async_task,
    )

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


@patch.object(AsyncJob, "queue")
def test_periodic_grievances_notifications_schedules_async_job(mock_queue: Mock) -> None:
    periodic_grievances_notifications_async_task()

    job = AsyncJob.objects.get()

    assert job.owner is None
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task_action"
    assert job.config == {}
    assert job.group_key == "grievance"
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
    job = create_async_job("hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task_action", {})

    periodic_grievances_notifications_async_task_action(job)

    sensitive_ticket.refresh_from_db()
    other_ticket.refresh_from_db()
    assert mock_notification_cls.call_count == 2
    assert sensitive_ticket.last_notification_sent is not None
    assert other_ticket.last_notification_sent is not None


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


# --- periodic_grievances_notifications_async_task tests ---


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
        category=category,
        issue_type=issue_type,
        status=status,
        last_notification_sent=last_notification_sent,
    )
    GrievanceTicket.objects.filter(pk=ticket.pk).update(
        created_at=timezone.now() - timedelta(days=created_days_ago),
    )
    return ticket


@patch("hope.apps.grievance.celery_tasks.GrievanceNotification")
def test_sensitive_ticket_notified_when_never_notified(mock_notification_cls: Mock) -> None:
    ticket = _make_ticket(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        created_days_ago=2,
    )

    periodic_grievances_notifications_async_task()

    # Verify called once and check first argument is the ticket
    mock_notification_cls.assert_called_once()
    call_args = mock_notification_cls.call_args
    assert call_args[0][0] == ticket
    mock_notification_cls.return_value.send_email_notification.assert_called_once()
    ticket.refresh_from_db()
    assert ticket.last_notification_sent is not None


@patch("hope.apps.grievance.celery_tasks.GrievanceNotification")
def test_sensitive_ticket_notified_when_last_sent_overdue(mock_notification_cls: Mock) -> None:
    ticket = _make_ticket(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        created_days_ago=5,
        last_notification_sent=timezone.now() - timedelta(days=2),
    )

    periodic_grievances_notifications_async_task()

    # Verify called once and check first argument is the ticket
    mock_notification_cls.assert_called_once()
    call_args = mock_notification_cls.call_args
    assert call_args[0][0] == ticket
    mock_notification_cls.return_value.send_email_notification.assert_called_once()


@patch("hope.apps.grievance.celery_tasks.GrievanceNotification")
def test_sensitive_ticket_skipped_when_email_disabled(mock_notification_cls: Mock) -> None:
    _make_ticket(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        created_days_ago=2,
        enable_email=False,
    )

    periodic_grievances_notifications_async_task()

    mock_notification_cls.return_value.send_email_notification.assert_not_called()


@patch("hope.apps.grievance.celery_tasks.GrievanceNotification")
def test_closed_ticket_excluded_from_notifications(mock_notification_cls: Mock) -> None:
    _make_ticket(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        status=GrievanceTicket.STATUS_CLOSED,
        created_days_ago=2,
    )

    periodic_grievances_notifications_async_task()

    mock_notification_cls.return_value.send_email_notification.assert_not_called()


@patch("hope.apps.grievance.celery_tasks.GrievanceNotification")
def test_other_ticket_notified_when_overdue(mock_notification_cls: Mock) -> None:
    ticket = _make_ticket(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        created_days_ago=31,
    )

    periodic_grievances_notifications_async_task()

    # Verify called once and check first argument is the ticket
    mock_notification_cls.assert_called_once()
    call_args = mock_notification_cls.call_args
    assert call_args[0][0] == ticket
    mock_notification_cls.return_value.send_email_notification.assert_called_once()
    ticket.refresh_from_db()
    assert ticket.last_notification_sent is not None


@patch("hope.apps.grievance.celery_tasks.GrievanceNotification")
def test_sensitive_ticket_excluded_from_other_notifications(mock_notification_cls: Mock) -> None:
    ticket = _make_ticket(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        created_days_ago=31,
    )

    periodic_grievances_notifications_async_task()

    # Sensitive ticket 31 days old matches 1-day threshold → ACTION_SENSITIVE_REMINDER only
    # Verify called once and check first argument is the ticket
    mock_notification_cls.assert_called_once()
    call_args = mock_notification_cls.call_args
    assert call_args[0][0] == ticket
