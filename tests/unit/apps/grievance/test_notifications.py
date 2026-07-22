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
    ProgramFactory,
    RoleFactory,
    TicketNoteFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.models import BusinessArea, Program, Role, User

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
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, name="Sensitive program")


@pytest.fixture
def other_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, name="Other program")


@pytest.fixture
def sensitive_ticket_in_program(business_area: BusinessArea, assignee: User, program: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )
    ticket.programs.set([program])
    return ticket


@pytest.fixture
def sensitive_role() -> Role:
    return RoleFactory(
        name="Sensitive Viewer",
        permissions=[
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE.value,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE.value,
        ],
    )


@pytest.fixture
def grievance_view_role() -> Role:
    return RoleFactory(
        name="Grievance Viewer",
        permissions=[
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE.value,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE.value,
        ],
    )


@pytest.fixture
def payment_verification_role() -> Role:
    return RoleFactory(
        name="Payment Verifier",
        permissions=[
            Permissions.PAYMENT_VERIFICATION_VIEW_LIST.value,
            Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS.value,
        ],
    )


@pytest.fixture
def payment_and_grievance_role() -> Role:
    return RoleFactory(
        name="Payment And Grievance Viewer",
        permissions=[
            Permissions.PAYMENT_VERIFICATION_VIEW_LIST.value,
            Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS.value,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE.value,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE.value,
        ],
    )


@pytest.fixture
def approve_data_change_role() -> Role:
    return RoleFactory(
        name="Data Change Approver",
        permissions=[Permissions.GRIEVANCES_APPROVE_DATA_CHANGE.value],
    )


@pytest.fixture
def approve_flag_and_dedupe_role() -> Role:
    return RoleFactory(
        name="Flag And Dedupe Approver",
        permissions=[Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE.value],
    )


@pytest.fixture
def approve_payment_verification_role() -> Role:
    return RoleFactory(
        name="Payment Verification Approver",
        permissions=[Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION.value],
    )


@pytest.fixture
def approve_data_change_as_creator_role() -> Role:
    return RoleFactory(
        name="Data Change Creator Approver",
        permissions=[Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR.value],
    )


@pytest.fixture
def approve_data_change_as_owner_role() -> Role:
    return RoleFactory(
        name="Data Change Owner Approver",
        permissions=[Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER.value],
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


def test_assignment_changed_recipient_targets_the_assignee(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)

    assert notification.user_recipients == [assignee]


def test_assignment_changed_recipient_excludes_editor_who_assigned_themselves(
    assigned_ticket: GrievanceTicket, assignee: User
) -> None:
    notification = GrievanceNotification(
        assigned_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED, editor=assignee
    )

    assert notification.user_recipients == []


@override_settings(ENV="prod")
def test_users_with_permissions_exclude_staff_and_superuser_in_prod(
    business_area: BusinessArea, sensitive_ticket: GrievanceTicket, sensitive_role: Role
) -> None:
    staff = UserFactory(email="staff@example.com", is_staff=True)
    UserRoleAssignmentFactory(user=staff, role=sensitive_role, business_area=business_area)

    superuser = UserFactory(email="super@example.com", is_superuser=True)
    UserRoleAssignmentFactory(user=superuser, role=sensitive_role, business_area=business_area)

    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == []


@override_settings(ENV="prod")
def test_users_with_permissions_keep_regular_users_in_prod(
    business_area: BusinessArea, sensitive_ticket: GrievanceTicket, sensitive_role: Role
) -> None:
    recipient = UserFactory(email="regular@example.com")
    UserRoleAssignmentFactory(user=recipient, role=sensitive_role, business_area=business_area)

    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_sensitive_created_excludes_the_actor(
    business_area: BusinessArea, sensitive_role: Role, assignee: User
) -> None:
    actor = UserFactory(email="creator-actor@example.com")
    UserRoleAssignmentFactory(user=actor, role=sensitive_role, business_area=business_area)
    other = UserFactory(email="other-viewer@example.com")
    UserRoleAssignmentFactory(user=other, role=sensitive_role, business_area=business_area)
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED, editor=actor)

    assert list(notification.user_recipients) == [other]


def test_prepare_notification_for_ticket_creation_excludes_actor_from_sensitive_recipients(
    business_area: BusinessArea, sensitive_role: Role
) -> None:
    actor = UserFactory(email="actor-clicker@example.com")
    UserRoleAssignmentFactory(user=actor, role=sensitive_role, business_area=business_area)
    other = UserFactory(email="other-sensitive-viewer@example.com")
    UserRoleAssignmentFactory(user=other, role=sensitive_role, business_area=business_area)
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=None,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )

    notifications = GrievanceNotification.prepare_notification_for_ticket_creation(ticket, actor=actor)

    assert len(notifications) == 1
    assert notifications[0].action == GrievanceNotification.ACTION_SENSITIVE_CREATED
    assert list(notifications[0].user_recipients) == [other]


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


def test_universal_category_recipients_excludes_assignee_and_expired(
    business_area: BusinessArea, grievance_view_role: Role
) -> None:
    recipient = UserFactory(email="recipient@example.com")
    UserRoleAssignmentFactory(user=recipient, role=grievance_view_role, business_area=business_area)

    expired = UserFactory(email="expired@example.com")
    UserRoleAssignmentFactory(
        user=expired,
        role=grievance_view_role,
        business_area=business_area,
        expiry_date=timezone.now() - timedelta(days=1),
    )

    assignee = UserFactory(email="assigned@example.com")
    UserRoleAssignmentFactory(user=assignee, role=grievance_view_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        assigned_to=assignee,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_for_approval_recipients_include_assignee_with_general_permission(
    business_area: BusinessArea, approve_data_change_role: Role
) -> None:
    approver = UserFactory(email="approver2@example.com")
    UserRoleAssignmentFactory(user=approver, role=approve_data_change_role, business_area=business_area)

    assignee = UserFactory(email="approver-assignee@example.com")
    UserRoleAssignmentFactory(user=assignee, role=approve_data_change_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area, category=GrievanceTicket.CATEGORY_DATA_CHANGE, assigned_to=assignee
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert {user.id for user in notification.user_recipients} == {approver.id, assignee.id}


def test_for_approval_recipients_without_assignee(business_area: BusinessArea, approve_data_change_role: Role) -> None:
    approver = UserFactory(email="approver3@example.com")
    UserRoleAssignmentFactory(user=approver, role=approve_data_change_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area, category=GrievanceTicket.CATEGORY_DATA_CHANGE, assigned_to=None
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [approver]


def test_universal_category_recipients_without_assignee(business_area: BusinessArea, grievance_view_role: Role) -> None:
    recipient = UserFactory(email="adjudicator@example.com")
    UserRoleAssignmentFactory(user=recipient, role=grievance_view_role, business_area=business_area)

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


def test_prepare_notification_for_ticket_creation_notifies_assignee_other_than_creator(
    business_area: BusinessArea, assignee: User, creator: User
) -> None:
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=assignee,
        created_by=creator,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
    )

    notifications = GrievanceNotification.prepare_notification_for_ticket_creation(ticket)

    assert len(notifications) == 1
    assert notifications[0].action == GrievanceNotification.ACTION_ASSIGNMENT_CHANGED
    assert notifications[0].user_recipients == [assignee]


def test_prepare_notification_for_ticket_creation_skips_assignment_email_for_self_assigning_creator(
    business_area: BusinessArea, creator: User
) -> None:
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        assigned_to=creator,
        created_by=creator,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
    )

    notifications = GrievanceNotification.prepare_notification_for_ticket_creation(ticket)

    assert notifications[0].user_recipients == []


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


def test_sensitive_created_recipients_exclude_role_scoped_to_other_program(
    business_area: BusinessArea,
    sensitive_ticket_in_program: GrievanceTicket,
    sensitive_role: Role,
    other_program: Program,
) -> None:
    wrong_program_user = UserFactory(email="wrong-program@example.com")
    UserRoleAssignmentFactory(
        user=wrong_program_user, role=sensitive_role, business_area=business_area, program=other_program
    )

    notification = GrievanceNotification(sensitive_ticket_in_program, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == []


def test_sensitive_created_recipients_include_role_scoped_to_ticket_program(
    business_area: BusinessArea,
    sensitive_ticket_in_program: GrievanceTicket,
    sensitive_role: Role,
    program: Program,
) -> None:
    recipient = UserFactory(email="right-program@example.com")
    UserRoleAssignmentFactory(user=recipient, role=sensitive_role, business_area=business_area, program=program)

    notification = GrievanceNotification(sensitive_ticket_in_program, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_sensitive_created_recipients_include_program_scoped_role_when_ticket_has_no_programs(
    business_area: BusinessArea,
    sensitive_ticket: GrievanceTicket,
    sensitive_role: Role,
    other_program: Program,
) -> None:
    recipient = UserFactory(email="scoped-but-no-ticket-program@example.com")
    UserRoleAssignmentFactory(user=recipient, role=sensitive_role, business_area=business_area, program=other_program)

    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_sensitive_created_recipients_exclude_inactive_and_blank_email_users(
    business_area: BusinessArea, sensitive_ticket: GrievanceTicket, sensitive_role: Role
) -> None:
    inactive = UserFactory(email="inactive@example.com", is_active=False)
    UserRoleAssignmentFactory(user=inactive, role=sensitive_role, business_area=business_area)

    no_email = UserFactory(email="", username="no_email_user")
    UserRoleAssignmentFactory(user=no_email, role=sensitive_role, business_area=business_area)

    notification = GrievanceNotification(sensitive_ticket, GrievanceNotification.ACTION_SENSITIVE_CREATED)

    assert list(notification.user_recipients) == []


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


def test_deduplication_recipients_use_grievance_view_permission(
    business_area: BusinessArea, grievance_view_role: Role
) -> None:
    recipient = UserFactory(email="dedupe-viewer@example.com")
    UserRoleAssignmentFactory(user=recipient, role=grievance_view_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_DEDUPLICATION_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_system_flagging_recipients_exclude_sensitive_only_permission(
    business_area: BusinessArea, sensitive_role: Role
) -> None:
    sensitive_only = UserFactory(email="sensitive-only@example.com")
    UserRoleAssignmentFactory(user=sensitive_only, role=sensitive_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED)

    assert list(notification.user_recipients) == []


def test_system_flagging_recipients_respect_program_scope(
    business_area: BusinessArea, grievance_view_role: Role, program: Program, other_program: Program
) -> None:
    in_program = UserFactory(email="in-program@example.com")
    UserRoleAssignmentFactory(user=in_program, role=grievance_view_role, business_area=business_area, program=program)

    out_of_program = UserFactory(email="out-program@example.com")
    UserRoleAssignmentFactory(
        user=out_of_program, role=grievance_view_role, business_area=business_area, program=other_program
    )

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        assigned_to=None,
    )
    ticket.programs.set([program])

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED)

    assert list(notification.user_recipients) == [in_program]


def test_payment_verification_recipients_require_both_permission_groups(
    business_area: BusinessArea, payment_and_grievance_role: Role
) -> None:
    recipient = UserFactory(email="pv-and-grievance@example.com")
    UserRoleAssignmentFactory(user=recipient, role=payment_and_grievance_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_payment_verification_recipients_exclude_grievance_permission_only(
    business_area: BusinessArea, grievance_view_role: Role
) -> None:
    grievance_only = UserFactory(email="grievance-only@example.com")
    UserRoleAssignmentFactory(user=grievance_only, role=grievance_view_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED)

    assert list(notification.user_recipients) == []


def test_payment_verification_recipients_exclude_payment_permission_only(
    business_area: BusinessArea, payment_verification_role: Role
) -> None:
    payment_only = UserFactory(email="payment-only@example.com")
    UserRoleAssignmentFactory(user=payment_only, role=payment_verification_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED)

    assert list(notification.user_recipients) == []


def test_payment_verification_recipients_allow_permissions_across_separate_roles(
    business_area: BusinessArea, grievance_view_role: Role, payment_verification_role: Role
) -> None:
    recipient = UserFactory(email="split-roles@example.com")
    UserRoleAssignmentFactory(user=recipient, role=grievance_view_role, business_area=business_area)
    UserRoleAssignmentFactory(user=recipient, role=payment_verification_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED)

    assert list(notification.user_recipients) == [recipient]


def test_for_approval_recipients_data_change_uses_data_change_permission(
    business_area: BusinessArea, approve_data_change_role: Role, approve_flag_and_dedupe_role: Role
) -> None:
    approver = UserFactory(email="dc-approver@example.com")
    UserRoleAssignmentFactory(user=approver, role=approve_data_change_role, business_area=business_area)

    wrong_approver = UserFactory(email="fd-approver@example.com")
    UserRoleAssignmentFactory(user=wrong_approver, role=approve_flag_and_dedupe_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area, category=GrievanceTicket.CATEGORY_DATA_CHANGE, assigned_to=None
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [approver]


def test_for_approval_recipients_system_flagging_uses_flag_and_dedupe_permission(
    business_area: BusinessArea, approve_flag_and_dedupe_role: Role
) -> None:
    approver = UserFactory(email="sf-approver@example.com")
    UserRoleAssignmentFactory(user=approver, role=approve_flag_and_dedupe_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [approver]


def test_for_approval_recipients_needs_adjudication_uses_flag_and_dedupe_permission(
    business_area: BusinessArea, approve_flag_and_dedupe_role: Role
) -> None:
    approver = UserFactory(email="na-approver@example.com")
    UserRoleAssignmentFactory(user=approver, role=approve_flag_and_dedupe_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [approver]


def test_for_approval_recipients_payment_verification_uses_payment_permission(
    business_area: BusinessArea, approve_payment_verification_role: Role
) -> None:
    approver = UserFactory(email="pv-approver@example.com")
    UserRoleAssignmentFactory(user=approver, role=approve_payment_verification_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [approver]


def test_for_approval_recipients_empty_for_category_without_approval(
    business_area: BusinessArea, approve_data_change_role: Role
) -> None:
    approver = UserFactory(email="referral-approver@example.com")
    UserRoleAssignmentFactory(user=approver, role=approve_data_change_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == []


def test_for_approval_recipients_include_creator_with_as_creator_permission(
    business_area: BusinessArea, approve_data_change_as_creator_role: Role
) -> None:
    creator = UserFactory(email="dc-creator-approver@example.com")
    UserRoleAssignmentFactory(user=creator, role=approve_data_change_as_creator_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        created_by=creator,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [creator]


def test_for_approval_recipients_exclude_non_creator_with_as_creator_permission(
    business_area: BusinessArea, approve_data_change_as_creator_role: Role
) -> None:
    non_creator = UserFactory(email="dc-noncreator@example.com")
    UserRoleAssignmentFactory(user=non_creator, role=approve_data_change_as_creator_role, business_area=business_area)
    creator = UserFactory(email="dc-actual-creator@example.com")

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        created_by=creator,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == []


def test_for_approval_recipients_include_owner_with_as_owner_permission(
    business_area: BusinessArea, approve_data_change_as_owner_role: Role
) -> None:
    owner = UserFactory(email="dc-owner-approver@example.com")
    UserRoleAssignmentFactory(user=owner, role=approve_data_change_as_owner_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        created_by=None,
        assigned_to=owner,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [owner]


def test_for_approval_recipients_exclude_non_owner_with_as_owner_permission(
    business_area: BusinessArea, approve_data_change_as_owner_role: Role
) -> None:
    non_owner = UserFactory(email="dc-nonowner@example.com")
    UserRoleAssignmentFactory(user=non_owner, role=approve_data_change_as_owner_role, business_area=business_area)
    owner = UserFactory(email="dc-actual-owner@example.com")

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        created_by=None,
        assigned_to=owner,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == []


def test_for_approval_recipients_exclude_owner_with_as_owner_who_performed_the_action(
    business_area: BusinessArea, approve_data_change_as_owner_role: Role
) -> None:
    owner = UserFactory(email="dc-owner-actor@example.com")
    UserRoleAssignmentFactory(user=owner, role=approve_data_change_as_owner_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        created_by=None,
        assigned_to=owner,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL, editor=owner)

    assert list(notification.user_recipients) == []


def test_for_approval_recipients_exclude_owner_without_permission(
    business_area: BusinessArea, approve_data_change_role: Role
) -> None:
    approver = UserFactory(email="dc-real-approver@example.com")
    UserRoleAssignmentFactory(user=approver, role=approve_data_change_role, business_area=business_area)

    owner_without_permission = UserFactory(email="dc-owner-noperm@example.com")

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        created_by=None,
        assigned_to=owner_without_permission,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [approver]


def test_for_approval_recipients_exclude_editor_who_performed_the_action(
    business_area: BusinessArea, approve_data_change_role: Role
) -> None:
    editor = UserFactory(email="dc-editor-approver@example.com")
    UserRoleAssignmentFactory(user=editor, role=approve_data_change_role, business_area=business_area)

    other_approver = UserFactory(email="dc-other-approver@example.com")
    UserRoleAssignmentFactory(user=other_approver, role=approve_data_change_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area, category=GrievanceTicket.CATEGORY_DATA_CHANGE, assigned_to=None
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL, editor=editor)

    assert list(notification.user_recipients) == [other_approver]
