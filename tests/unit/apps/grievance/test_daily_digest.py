from datetime import UTC, datetime
import json
from typing import Any, Callable
from unittest.mock import patch

from constance.test import override_config
from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.celery_tasks import (
    daily_grievance_digest_async_task,
    daily_grievance_digest_async_task_action,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services import daily_digest_service
from hope.apps.grievance.services.daily_digest_service import DailyDigestService
from hope.models import BusinessArea, Partner, PeriodicAsyncJob, Program, User

pytestmark = pytest.mark.django_db

DIGEST_DATE = datetime(2026, 8, 9, tzinfo=UTC).date()
DURING_THE_DAY = datetime(2026, 8, 9, 10, 30, tzinfo=UTC)
NEXT_DAY = datetime(2026, 8, 10, 10, 30, tzinfo=UTC)


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", enable_email_notification=True)


@pytest.fixture
def other_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="ukraine", name="Ukraine", enable_email_notification=True)


@pytest.fixture
def silent_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="somalia", name="Somalia", enable_email_notification=False)


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE, name="program afghanistan 1")


@pytest.fixture
def assignee() -> User:
    return UserFactory(first_name="As", last_name="Signee", email="assignee@example.com")


@pytest.fixture
def creator() -> User:
    return UserFactory(first_name="Cre", last_name="Ator", email="creator@example.com")


@pytest.fixture
def actor(partner: Partner) -> User:
    return UserFactory(first_name="Ac", last_name="Tor", email="actor@example.com", partner=partner)


@pytest.fixture
def assigned_ticket(business_area: BusinessArea, assignee: User, actor: User) -> GrievanceTicket:
    return GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
    )


@pytest.fixture
def edited_ticket(business_area: BusinessArea, assignee: User, creator: User, actor: User) -> GrievanceTicket:
    return GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        created_by=creator,
        user_modified=DURING_THE_DAY,
        user_modified_by=actor,
    )


@pytest.fixture
def bulk_assign_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-bulk-update-assignee",
        kwargs={"business_area_slug": business_area.slug},
    )


def test_assigned_ticket_is_listed_to_its_assignee(
    business_area: BusinessArea, assigned_ticket: GrievanceTicket, assignee: User
) -> None:
    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert len(digests) == 1
    assert digests[0].user == assignee
    assert digests[0].assigned == [assigned_ticket]
    assert digests[0].edited == []


def test_edited_ticket_is_listed_to_creator_and_assignee(
    business_area: BusinessArea, edited_ticket: GrievanceTicket, assignee: User, creator: User
) -> None:
    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert {digest.user for digest in digests} == {assignee, creator}
    assert all(digest.edited == [edited_ticket] for digest in digests)


def test_edited_ticket_is_not_listed_to_its_own_editor(
    business_area: BusinessArea, assignee: User, creator: User
) -> None:
    GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        created_by=creator,
        user_modified=DURING_THE_DAY,
        user_modified_by=assignee,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert [digest.user for digest in digests] == [creator]


def test_ticket_created_during_the_window_is_not_listed_as_edited(
    business_area: BusinessArea, assignee: User, creator: User
) -> None:
    GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        created_by=creator,
        user_modified=DURING_THE_DAY,
        user_modified_by=None,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert digests == []


def test_self_assignment_is_not_listed_to_the_self_assigner(business_area: BusinessArea, assignee: User) -> None:
    GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=assignee,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert digests == []


def test_assignment_by_a_deleted_user_is_still_listed(business_area: BusinessArea, assignee: User, actor: User) -> None:
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
    )
    actor.delete()

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert len(digests) == 1
    assert digests[0].assigned == [ticket]


def test_unassignment_produces_no_digest(business_area: BusinessArea, actor: User) -> None:
    GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=None,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert digests == []


def test_ticket_in_both_buckets_is_listed_once_under_assigned(
    business_area: BusinessArea, assignee: User, actor: User
) -> None:
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
        user_modified=DURING_THE_DAY,
        user_modified_by=actor,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert len(digests) == 1
    assert digests[0].assigned == [ticket]
    assert digests[0].edited == []


def test_ticket_closed_after_the_window_is_still_listed(
    business_area: BusinessArea, assignee: User, actor: User
) -> None:
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
        status=GrievanceTicket.STATUS_CLOSED,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert digests[0].assigned == [ticket]


def test_assignment_outside_the_window_is_not_listed(business_area: BusinessArea, assignee: User, actor: User) -> None:
    GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        assigned_at=NEXT_DAY,
        assigned_by=actor,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert digests == []


def test_tickets_from_another_business_area_are_not_listed(
    business_area: BusinessArea,
    other_business_area: BusinessArea,
    assigned_ticket: GrievanceTicket,
    assignee: User,
    actor: User,
) -> None:
    GrievanceTicketFactory(
        business_area=other_business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert digests[0].assigned == [assigned_ticket]


def test_business_area_with_email_notification_disabled_lists_nothing(
    silent_business_area: BusinessArea, assignee: User, actor: User
) -> None:
    GrievanceTicketFactory(
        business_area=silent_business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
    )

    digests = DailyDigestService(silent_business_area, DIGEST_DATE).build_digests()

    assert digests == []


def test_inactive_assignee_is_not_listed(business_area: BusinessArea, actor: User) -> None:
    GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=UserFactory(email="inactive@example.com", is_active=False),
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert digests == []


def test_assignee_without_an_email_is_not_listed(business_area: BusinessArea, actor: User) -> None:
    GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=UserFactory(email=""),
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
    )

    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()

    assert digests == []


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_no_email_is_sent_when_both_buckets_are_empty(business_area: BusinessArea) -> None:
    with patch.object(daily_digest_service.MailjetClient, "send_email") as mock_send:
        sent, failed = DailyDigestService(business_area, DIGEST_DATE).send()

    mock_send.assert_not_called()
    assert (sent, failed) == (0, 0)


@override_config(SEND_GRIEVANCES_NOTIFICATION=False)
def test_no_email_is_sent_when_the_global_flag_is_off(
    business_area: BusinessArea, assigned_ticket: GrievanceTicket
) -> None:
    with patch.object(daily_digest_service.MailjetClient, "send_email") as mock_send:
        sent, failed = DailyDigestService(business_area, DIGEST_DATE).send()

    mock_send.assert_not_called()
    assert (sent, failed) == (0, 0)


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_one_email_per_recipient_is_sent(business_area: BusinessArea, edited_ticket: GrievanceTicket) -> None:
    with patch.object(daily_digest_service.MailjetClient, "send_email") as mock_send:
        sent, failed = DailyDigestService(business_area, DIGEST_DATE).send()

    assert mock_send.call_count == 2
    assert (sent, failed) == (2, 0)


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_a_failing_recipient_does_not_stop_the_others(
    business_area: BusinessArea, edited_ticket: GrievanceTicket
) -> None:
    with patch.object(daily_digest_service.MailjetClient, "send_email", side_effect=[Exception("boom"), None]):
        sent, failed = DailyDigestService(business_area, DIGEST_DATE).send()

    assert (sent, failed) == (1, 1)


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
@patch("hope.apps.utils.celery_tasks.requests.post")
def test_payload_lists_the_ticket_with_a_link(
    mocked_requests_post: Any, business_area: BusinessArea, assigned_ticket: GrievanceTicket, assignee: User
) -> None:
    mocked_requests_post.return_value.status_code = 200

    DailyDigestService(business_area, DIGEST_DATE).send()

    message = json.loads(mocked_requests_post.call_args.kwargs["data"])["Messages"][0]
    assert message["To"] == [{"Email": assignee.email}]
    assert assigned_ticket.unicef_id in message["HTMLPart"]
    assert "<a href" in message["HTMLPart"]
    assert "2026-08-09" in message["Subject"]
    assert "2026-08-09" in message["HTMLPart"]


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
@patch("hope.apps.utils.celery_tasks.requests.post")
def test_payload_omits_the_link_for_a_sensitive_ticket(
    mocked_requests_post: Any, business_area: BusinessArea, assignee: User, actor: User
) -> None:
    mocked_requests_post.return_value.status_code = 200
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )

    DailyDigestService(business_area, DIGEST_DATE).send()

    message = json.loads(mocked_requests_post.call_args.kwargs["data"])["Messages"][0]
    assert ticket.unicef_id in message["HTMLPart"]
    assert "<a href" not in message["HTMLPart"]
    assert "http" not in message["TextPart"]


@override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
@patch("hope.apps.utils.celery_tasks.requests.post")
def test_row_cap_summarises_the_remainder(
    mocked_requests_post: Any, business_area: BusinessArea, assignee: User, actor: User
) -> None:
    mocked_requests_post.return_value.status_code = 200
    GrievanceTicketFactory.create_batch(
        DailyDigestService.ROW_LIMIT + 3,
        business_area=business_area,
        assigned_to=assignee,
        assigned_at=DURING_THE_DAY,
        assigned_by=actor,
    )

    DailyDigestService(business_area, DIGEST_DATE).send()

    message = json.loads(mocked_requests_post.call_args.kwargs["data"])["Messages"][0]
    assert message["HTMLPart"].count("<li>") == DailyDigestService.ROW_LIMIT + 1
    assert "and 3 more" in message["TextPart"]


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_fan_out_queues_one_job_per_enabled_business_area(
    business_area: BusinessArea, other_business_area: BusinessArea, silent_business_area: BusinessArea
) -> None:
    with patch("hope.apps.grievance.celery_tasks.PeriodicAsyncJob.queue_task") as mock_queue_task:
        daily_grievance_digest_async_task()

    queued_business_area_ids = {call.kwargs["config"]["business_area_id"] for call in mock_queue_task.call_args_list}
    assert str(business_area.id) in queued_business_area_ids
    assert str(other_business_area.id) in queued_business_area_ids
    assert str(silent_business_area.id) not in queued_business_area_ids
    assert all(
        call.kwargs["action"] == "hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action"
        for call in mock_queue_task.call_args_list
    )


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_fan_out_pins_yesterday_as_the_digest_date(business_area: BusinessArea) -> None:
    with patch("hope.apps.grievance.celery_tasks.PeriodicAsyncJob.queue_task") as mock_queue_task:
        with freeze_time(NEXT_DAY):
            daily_grievance_digest_async_task()

    assert mock_queue_task.call_args.kwargs["config"]["digest_date"] == "2026-08-09"


@override_config(SEND_GRIEVANCES_NOTIFICATION=False)
def test_fan_out_queues_nothing_when_the_global_flag_is_off(business_area: BusinessArea) -> None:
    with patch("hope.apps.grievance.celery_tasks.PeriodicAsyncJob.queue_task") as mock_queue_task:
        daily_grievance_digest_async_task()

    mock_queue_task.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_action_sends_the_digest_for_the_pinned_business_area_and_day(
    business_area: BusinessArea, assigned_ticket: GrievanceTicket
) -> None:
    job = PeriodicAsyncJob.objects.create(
        type=PeriodicAsyncJob.JobType.JOB_TASK,
        job_name="daily_grievance_digest_async_task",
        action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
        config={"business_area_id": str(business_area.id), "digest_date": "2026-08-09"},
    )

    with patch.object(daily_digest_service.MailjetClient, "send_email") as mock_send:
        daily_grievance_digest_async_task_action(job)

    mock_send.assert_called_once()
    job.refresh_from_db()
    assert job.config["completed_for"] == f"{business_area.id}:2026-08-09"


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_rerunning_the_same_job_sends_nothing(business_area: BusinessArea, assigned_ticket: GrievanceTicket) -> None:
    job = PeriodicAsyncJob.objects.create(
        type=PeriodicAsyncJob.JobType.JOB_TASK,
        job_name="daily_grievance_digest_async_task",
        action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
        config={"business_area_id": str(business_area.id), "digest_date": "2026-08-09"},
    )

    with patch.object(daily_digest_service.MailjetClient, "send_email") as mock_send:
        daily_grievance_digest_async_task_action(job)
        daily_grievance_digest_async_task_action(job)

    assert mock_send.call_count == 1


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_a_second_job_for_a_finished_day_sends_nothing(
    business_area: BusinessArea, assigned_ticket: GrievanceTicket
) -> None:
    PeriodicAsyncJob.objects.create(
        type=PeriodicAsyncJob.JobType.JOB_TASK,
        job_name="daily_grievance_digest_async_task",
        action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
        config={
            "business_area_id": str(business_area.id),
            "digest_date": "2026-08-09",
            "completed_for": f"{business_area.id}:2026-08-09",
        },
    )
    duplicate_job = PeriodicAsyncJob.objects.create(
        type=PeriodicAsyncJob.JobType.JOB_TASK,
        job_name="daily_grievance_digest_async_task",
        action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
        config={"business_area_id": str(business_area.id), "digest_date": "2026-08-09"},
    )

    with patch.object(daily_digest_service.MailjetClient, "send_email") as mock_send:
        daily_grievance_digest_async_task_action(duplicate_job)

    mock_send.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_failed_send_leaves_the_day_unmarked(business_area: BusinessArea, assigned_ticket: GrievanceTicket) -> None:
    job = PeriodicAsyncJob.objects.create(
        type=PeriodicAsyncJob.JobType.JOB_TASK,
        job_name="daily_grievance_digest_async_task",
        action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
        config={"business_area_id": str(business_area.id), "digest_date": "2026-08-09"},
    )

    with patch.object(daily_digest_service.MailjetClient, "send_email", side_effect=Exception("boom")):
        with pytest.raises(RuntimeError, match="1 recipient"):
            daily_grievance_digest_async_task_action(job)

    job.refresh_from_db()
    assert "completed_for" not in job.config


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_failed_day_is_delivered_by_later_run(business_area: BusinessArea, assigned_ticket: GrievanceTicket) -> None:
    job = PeriodicAsyncJob.objects.create(
        type=PeriodicAsyncJob.JobType.JOB_TASK,
        job_name="daily_grievance_digest_async_task",
        action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
        config={"business_area_id": str(business_area.id), "digest_date": "2026-08-09"},
    )
    with patch.object(daily_digest_service.MailjetClient, "send_email", side_effect=Exception("boom")):
        with pytest.raises(RuntimeError):
            daily_grievance_digest_async_task_action(job)

    with patch.object(daily_digest_service.MailjetClient, "send_email") as mock_send:
        daily_grievance_digest_async_task_action(job)

    mock_send.assert_called_once()
    job.refresh_from_db()
    assert job.config["completed_for"] == f"{business_area.id}:2026-08-09"


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_action_skips_a_business_area_that_no_longer_exists() -> None:
    job = PeriodicAsyncJob.objects.create(
        type=PeriodicAsyncJob.JobType.JOB_TASK,
        job_name="daily_grievance_digest_async_task",
        action="hope.apps.grievance.celery_tasks.daily_grievance_digest_async_task_action",
        config={"business_area_id": "11111111-1111-1111-1111-111111111111", "digest_date": "2026-08-09"},
    )

    with patch.object(daily_digest_service.MailjetClient, "send_email") as mock_send:
        daily_grievance_digest_async_task_action(job)

    mock_send.assert_not_called()
    job.refresh_from_db()
    assert "completed_for" not in job.config


def test_bulk_assign_endpoint_feeds_the_digest(
    api_client: Any,
    business_area: BusinessArea,
    program: Program,
    actor: User,
    assignee: User,
    bulk_assign_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(actor, [Permissions.GRIEVANCES_UPDATE], business_area, program=program)
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=None)
    ticket.programs.set([program])

    with freeze_time(DURING_THE_DAY):
        response = api_client(actor).post(
            bulk_assign_url,
            {"grievance_ticket_ids": [str(ticket.id)], "assigned_to": str(assignee.id)},
            format="json",
        )

    assert response.status_code == status.HTTP_202_ACCEPTED
    ticket.refresh_from_db()
    assert ticket.assigned_at == DURING_THE_DAY
    digests = DailyDigestService(business_area, DIGEST_DATE).build_digests()
    assert len(digests) == 1
    assert digests[0].user == assignee
    assert digests[0].assigned == [ticket]


def test_bulk_assign_of_already_assigned_tickets_feeds_nothing(
    api_client: Any,
    business_area: BusinessArea,
    program: Program,
    actor: User,
    assignee: User,
    bulk_assign_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(actor, [Permissions.GRIEVANCES_UPDATE], business_area, program=program)
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=assignee)
    ticket.programs.set([program])

    with freeze_time(DURING_THE_DAY):
        response = api_client(actor).post(
            bulk_assign_url,
            {"grievance_ticket_ids": [str(ticket.id)], "assigned_to": str(assignee.id)},
            format="json",
        )

    assert response.status_code == status.HTTP_202_ACCEPTED
    ticket.refresh_from_db()
    assert ticket.assigned_at is None
    assert DailyDigestService(business_area, DIGEST_DATE).build_digests() == []
