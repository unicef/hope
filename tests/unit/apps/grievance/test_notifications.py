from datetime import timedelta
import json
from typing import Any
from unittest.mock import patch

from constance.test import override_config
from django.test import override_settings
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    PartnerFactory,
    PartnerRoleAssignmentFactory,
    RoleFactory,
    TicketNoteFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.models import BusinessArea, Role, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(enable_email_notification=True)


@pytest.fixture
def assignee() -> User:
    return UserFactory(first_name="As", last_name="Signee", email="assignee@example.com")


@pytest.fixture
def assigned_ticket(business_area: BusinessArea, assignee: User) -> GrievanceTicket:
    return GrievanceTicketFactory(business_area=business_area, assigned_to=assignee)


@pytest.fixture
def creator() -> User:
    return UserFactory(first_name="Cre", last_name="Ator", email="creator@example.com")


@pytest.fixture
def editor() -> User:
    return UserFactory(first_name="Ed", last_name="Itor", email="editor@example.com")


@pytest.fixture
def sensitive_ticket(business_area: BusinessArea, assignee: User) -> GrievanceTicket:
    return GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )


@pytest.fixture
def sensitive_role() -> Role:
    return RoleFactory(
        name="Sensitive Viewer",
        permissions=[
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE.value,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE.value,
        ],
    )


def test_init_builds_recipients_and_emails_for_assignment_changed(
    assigned_ticket: GrievanceTicket, assignee: User
) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    assert notification.user_recipients == [assignee]
    assert len(notification.emails) == 1
    assert notification.emails[0].recipients == [assignee.email]
    assert notification.enable_email_notification is True


def test_assigned_to_recipient_returns_empty_when_unassigned(business_area: BusinessArea) -> None:
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=None)

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory())

    assert notification.user_recipients == []
    assert notification.emails == []


@override_settings(SOCIAL_AUTH_REDIRECT_IS_HTTPS=True)
def test_default_context_uses_https_when_redirect_is_https(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    context = notification._prepare_default_context(assignee)

    assert context["ticket_url"].startswith("https://")
    assert context["ticket_id"] == assigned_ticket.unicef_id
    assert context["first_name"] == assignee.first_name


@override_settings(SOCIAL_AUTH_REDIRECT_IS_HTTPS=False)
def test_default_context_uses_http_when_redirect_not_https(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    context = notification._prepare_default_context(assignee)

    assert context["ticket_url"].startswith("http://")


def test_universal_category_recipients_excludes_assignee_and_expired(business_area: BusinessArea) -> None:
    adjudicator_role = RoleFactory(name="Adjudicator")
    recipient = UserFactory(email="recipient@example.com")
    UserRoleAssignmentFactory(user=recipient, role=adjudicator_role, business_area=business_area)

    expired = UserFactory(email="expired@example.com")
    UserRoleAssignmentFactory(
        user=expired,
        role=adjudicator_role,
        business_area=business_area,
        expiry_date=timezone.now() - timedelta(days=1),
    )

    assignee = UserFactory(email="assigned@example.com")
    UserRoleAssignmentFactory(user=assignee, role=adjudicator_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        assigned_to=assignee,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_for_approval_recipients_excludes_assignee(business_area: BusinessArea) -> None:
    approver_role = RoleFactory(name="Approver")
    approver = UserFactory(email="approver2@example.com")
    UserRoleAssignmentFactory(user=approver, role=approver_role, business_area=business_area)

    assignee = UserFactory(email="approver-assignee@example.com")
    UserRoleAssignmentFactory(user=assignee, role=approver_role, business_area=business_area)

    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=assignee)

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [approver]


def test_for_approval_recipients_without_assignee(business_area: BusinessArea) -> None:
    approver_role = RoleFactory(name="Approver")
    approver = UserFactory(email="approver3@example.com")
    UserRoleAssignmentFactory(user=approver, role=approver_role, business_area=business_area)

    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=None)

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [approver]


def test_universal_category_recipients_without_assignee(business_area: BusinessArea) -> None:
    adjudicator_role = RoleFactory(name="Adjudicator")
    recipient = UserFactory(email="adjudicator@example.com")
    UserRoleAssignmentFactory(user=recipient, role=adjudicator_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_sensitive_reminder_body_includes_hours_ago(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    GrievanceTicket.objects.filter(pk=assigned_ticket.pk).update(created_at=timezone.now() - timedelta(days=2))
    assigned_ticket.refresh_from_db()

    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_SENSITIVE_REMINDER)
    text_body, html_body, subject = notification._prepare_sensitive_reminder_bodies(assignee)

    assert assigned_ticket.unicef_id in subject
    assert "48 hours ago" in text_body
    assert "48 hours ago" in html_body


def test_overdue_body_includes_days_ago(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    GrievanceTicket.objects.filter(pk=assigned_ticket.pk).update(created_at=timezone.now() - timedelta(days=3))
    assigned_ticket.refresh_from_db()

    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_OVERDUE)
    text_body, html_body, subject = notification._prepare_overdue_bodies(assignee)

    assert assigned_ticket.unicef_id in subject
    assert "3 days ago" in text_body
    assert "3 days ago" in html_body


def test_add_note_body_uses_created_by_and_note(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    author = UserFactory(first_name="Note", last_name="Author")
    ticket_note = TicketNoteFactory(ticket=assigned_ticket, description="Please review the attached documents")

    notification = GrievanceNotification(
        assigned_ticket,
        GrievanceNotification.ACTION_NOTES_ADDED,
        created_by=author,
        ticket_note=ticket_note,
    )
    text_body, html_body, subject = notification._prepare_add_note_bodies(assignee)

    assert assigned_ticket.unicef_id in subject
    assert "Note Author" in text_body
    assert "Please review the attached documents" in text_body
    assert "Note Author" in html_body
    assert "Please review the attached documents" in html_body


def test_send_back_to_in_progress_body_uses_approver(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    approver = UserFactory(first_name="Ap", last_name="Prover")

    notification = GrievanceNotification(
        assigned_ticket,
        GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS,
        approver=approver,
    )
    text_body, html_body, subject = notification._prepare_send_back_to_in_progress_bodies(assignee)

    assert assigned_ticket.unicef_id in subject
    assert "Ap Prover" in text_body
    assert "Ap Prover" in html_body


def test_for_approval_body(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    text_body, html_body, subject = notification._prepare_for_approval_bodies(assignee)

    assert assigned_ticket.unicef_id in subject
    assert text_body
    assert html_body


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_send_email_notification_sends_when_enabled(assigned_ticket: GrievanceTicket) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    with patch.object(notification.emails[0], "send_email") as mock_send:
        notification.send_email_notification()

    mock_send.assert_called_once()


@override_config(SEND_GRIEVANCES_NOTIFICATION=False)
def test_send_email_notification_skipped_when_config_off(assigned_ticket: GrievanceTicket) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    with patch.object(notification.emails[0], "send_email") as mock_send:
        notification.send_email_notification()

    mock_send.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_send_email_notification_skipped_when_business_area_disabled(assignee: User) -> None:
    business_area = BusinessAreaFactory(enable_email_notification=False)
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=assignee)
    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    with patch.object(notification.emails[0], "send_email") as mock_send:
        notification.send_email_notification()

    mock_send.assert_not_called()


def test_prepare_notification_for_ticket_creation_assigned_and_category(
    business_area: BusinessArea, assignee: User
) -> None:
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
    )

    notifications = GrievanceNotification.prepare_notification_for_ticket_creation(ticket)

    actions = {n.action for n in notifications}
    assert GrievanceNotification.ACTION_ASSIGNMENT_CHANGED in actions
    assert GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED in actions


def test_prepare_notification_for_ticket_creation_no_assignee_no_matching_category(business_area: BusinessArea) -> None:
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=None,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
    )

    notifications = GrievanceNotification.prepare_notification_for_ticket_creation(ticket)

    assert notifications == []


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_send_all_notifications_sends_each(assigned_ticket: GrievanceTicket) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    with patch.object(notification.emails[0], "send_email") as mock_send:
        GrievanceNotification.send_all_notifications([notification])

    mock_send.assert_called_once()


def test_sensitive_created_recipients_from_user_permission(
    business_area: BusinessArea, sensitive_ticket: GrievanceTicket, sensitive_role: Role
) -> None:
    recipient = UserFactory(email="sensitive-viewer@example.com")
    UserRoleAssignmentFactory(user=recipient, role=sensitive_role, business_area=business_area)

    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_sensitive_created_recipients_match_on_either_permission(
    business_area: BusinessArea, sensitive_ticket: GrievanceTicket
) -> None:
    list_only_role = RoleFactory(
        name="List Only Sensitive",
        permissions=[Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE.value],
    )
    recipient = UserFactory(email="list-only@example.com")
    UserRoleAssignmentFactory(user=recipient, role=list_only_role, business_area=business_area)

    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_sensitive_created_recipients_from_partner_permission(
    business_area: BusinessArea, sensitive_ticket: GrievanceTicket, sensitive_role: Role
) -> None:
    partner = PartnerFactory(name="Sensitive Partner")
    PartnerRoleAssignmentFactory(partner=partner, role=sensitive_role, business_area=business_area)
    recipient = UserFactory(email="partner-user@example.com", partner=partner)

    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_sensitive_created_recipients_excludes_assignee_expired_and_unpermitted(
    business_area: BusinessArea, sensitive_ticket: GrievanceTicket, sensitive_role: Role, assignee: User
) -> None:
    UserRoleAssignmentFactory(user=assignee, role=sensitive_role, business_area=business_area)

    expired = UserFactory(email="expired-sensitive@example.com")
    UserRoleAssignmentFactory(
        user=expired,
        role=sensitive_role,
        business_area=business_area,
        expiry_date=timezone.now() - timedelta(days=1),
    )

    unrelated_role = RoleFactory(name="No Sensitive", permissions=[Permissions.GRIEVANCES_CREATE.value])
    unpermitted = UserFactory(email="no-sensitive@example.com")
    UserRoleAssignmentFactory(user=unpermitted, role=unrelated_role, business_area=business_area)

    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == []


def test_default_context_drops_url_for_sensitive_ticket(sensitive_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    context = notification._prepare_default_context(assignee)

    assert context["ticket_url"] is None
    assert context["ticket_id"] == sensitive_ticket.unicef_id


def test_assignment_body_omits_link_for_sensitive_ticket(sensitive_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    text_body, html_body, _ = notification._prepare_assignment_changed_bodies(assignee)

    assert "<a href" not in html_body
    assert sensitive_ticket.unicef_id in html_body
    assert "http" not in text_body


def test_assignment_body_keeps_link_for_non_sensitive_ticket(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    _, html_body, _ = notification._prepare_assignment_changed_bodies(assignee)

    assert "<a href" in html_body


def test_ticket_updated_recipients_creator_and_assignee_exclude_editor(
    business_area: BusinessArea, assignee: User, creator: User, editor: User
) -> None:
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=assignee, created_by=creator)

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_TICKET_UPDATED, editor=editor)

    assert {user.id for user in notification.user_recipients} == {creator.id, assignee.id}


def test_ticket_updated_recipients_exclude_editor_who_is_creator(
    business_area: BusinessArea, assignee: User, creator: User
) -> None:
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=assignee, created_by=creator)

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_TICKET_UPDATED, editor=creator)

    assert notification.user_recipients == [assignee]


def test_ticket_updated_body_states_change_without_details(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_TICKET_UPDATED)

    text_body, html_body, subject = notification._prepare_ticket_updated_bodies(assignee)

    assert assigned_ticket.unicef_id in subject
    assert "Changes have been made" in html_body
    assert "Changes have been made" in text_body


@patch("hope.apps.utils.celery_tasks.requests.post")
@override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
def test_sensitive_ticket_payload_sent_to_mailjet_has_no_link(
    mocked_requests_post: Any, sensitive_ticket: GrievanceTicket, assignee: User
) -> None:
    mocked_requests_post.return_value.status_code = 200
    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    notification.send_email_notification()

    message = json.loads(mocked_requests_post.call_args.kwargs["data"])["Messages"][0]
    assert message["To"] == [{"Email": assignee.email}]
    assert sensitive_ticket.unicef_id in message["HTMLPart"]
    assert "<a href" not in message["HTMLPart"]
    assert "http" not in message["TextPart"]


@patch("hope.apps.utils.celery_tasks.requests.post")
@override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
def test_non_sensitive_ticket_payload_sent_to_mailjet_keeps_link(
    mocked_requests_post: Any, assigned_ticket: GrievanceTicket
) -> None:
    mocked_requests_post.return_value.status_code = 200
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    notification.send_email_notification()

    message = json.loads(mocked_requests_post.call_args.kwargs["data"])["Messages"][0]
    assert assigned_ticket.unicef_id in message["HTMLPart"]
    assert "<a href" in message["HTMLPart"]
