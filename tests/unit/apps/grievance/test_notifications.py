import json
from typing import Any
from unittest.mock import patch

from constance.test import override_config
from django.test import override_settings
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
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


@pytest.fixture
def close_ticket_role() -> Role:
    return RoleFactory(
        name="Ticket Closer",
        permissions=[Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK.value],
    )


@pytest.fixture
def close_ticket_as_creator_role() -> Role:
    return RoleFactory(
        name="Ticket Closer Creator",
        permissions=[Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR.value],
    )


@pytest.fixture
def close_feedback_ticket_role() -> Role:
    return RoleFactory(
        name="Feedback Ticket Closer",
        permissions=[Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK.value],
    )


def test_init_builds_recipients_and_emails_for_sensitive_reminder(
    assigned_ticket: GrievanceTicket, assignee: User
) -> None:
    notification = GrievanceNotification(
        assigned_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

    assert notification.user_recipients == [assignee]
    assert len(notification.emails) == 1
    assert notification.emails[0].recipients == [assignee.email]
    assert notification.enable_email_notification is True


def test_assigned_to_recipient_returns_empty_when_unassigned(business_area: BusinessArea) -> None:
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=None)

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory())

    assert notification.user_recipients == []
    assert notification.emails == []


def test_assigned_to_recipient_excludes_inactive_assignee(business_area: BusinessArea) -> None:
    inactive_assignee = UserFactory(email="inactive-assignee@example.com", is_active=False)
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=inactive_assignee)

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory())

    assert notification.user_recipients == []
    assert notification.emails == []


def test_assigned_to_recipient_excludes_assignee_without_email(business_area: BusinessArea) -> None:
    no_email_assignee = UserFactory(email="")
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=no_email_assignee)

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory())

    assert notification.user_recipients == []
    assert notification.emails == []


def test_note_added_recipient_excludes_assignee_who_wrote_the_note(
    assigned_ticket: GrievanceTicket, assignee: User
) -> None:
    notification = GrievanceNotification(
        assigned_ticket,
        GrievanceNotification.ACTION_NOTES_ADDED,
        created_by=assignee,
        editor=assignee,
    )

    assert notification.user_recipients == []
    assert notification.emails == []


@override_settings(SOCIAL_AUTH_REDIRECT_IS_HTTPS=True)
def test_default_context_uses_https_when_redirect_is_https(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(
        assigned_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

    context = notification._prepare_default_context(assignee)

    assert context["ticket_url"].startswith("https://")
    assert context["ticket_id"] == assigned_ticket.unicef_id
    assert context["first_name"] == assignee.first_name


@override_settings(SOCIAL_AUTH_REDIRECT_IS_HTTPS=False)
def test_default_context_uses_http_when_redirect_not_https(assigned_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(
        assigned_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

    context = notification._prepare_default_context(assignee)

    assert context["ticket_url"].startswith("http://")


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
    notification = GrievanceNotification(assigned_ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    text_body, html_body, subject = notification._prepare_for_approval_bodies(assignee)

    assert assigned_ticket.unicef_id in subject
    assert text_body
    assert html_body


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_send_email_notification_sends_when_enabled(assigned_ticket: GrievanceTicket) -> None:
    notification = GrievanceNotification(
        assigned_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

    with patch.object(notification.emails[0], "send_email") as mock_send:
        notification.send_email_notification()

    mock_send.assert_called_once()


@override_config(SEND_GRIEVANCES_NOTIFICATION=False)
def test_send_email_notification_skipped_when_config_off(assigned_ticket: GrievanceTicket) -> None:
    notification = GrievanceNotification(
        assigned_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

    with patch.object(notification.emails[0], "send_email") as mock_send:
        notification.send_email_notification()

    mock_send.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_send_email_notification_skipped_when_business_area_disabled(assignee: User) -> None:
    business_area = BusinessAreaFactory(enable_email_notification=False)
    ticket = GrievanceTicketFactory(business_area=business_area, assigned_to=assignee)
    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory())

    with patch.object(notification.emails[0], "send_email") as mock_send:
        notification.send_email_notification()

    mock_send.assert_not_called()


@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_send_all_notifications_sends_each(assigned_ticket: GrievanceTicket) -> None:
    notification = GrievanceNotification(
        assigned_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

    with patch.object(notification.emails[0], "send_email") as mock_send:
        GrievanceNotification.send_all_notifications([notification])

    mock_send.assert_called_once()


def test_default_context_drops_url_for_sensitive_ticket(sensitive_ticket: GrievanceTicket, assignee: User) -> None:
    notification = GrievanceNotification(
        sensitive_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

    context = notification._prepare_default_context(assignee)

    assert context["ticket_url"] is None
    assert context["ticket_id"] == sensitive_ticket.unicef_id


@patch("hope.apps.utils.celery_tasks.requests.post")
@override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
def test_sensitive_ticket_payload_sent_to_mailjet_has_no_link(
    mocked_requests_post: Any, sensitive_ticket: GrievanceTicket, assignee: User
) -> None:
    mocked_requests_post.return_value.status_code = 200
    notification = GrievanceNotification(
        sensitive_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

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
    notification = GrievanceNotification(
        assigned_ticket, GrievanceNotification.ACTION_NOTES_ADDED, created_by=UserFactory()
    )

    notification.send_email_notification()

    message = json.loads(mocked_requests_post.call_args.kwargs["data"])["Messages"][0]
    assert assigned_ticket.unicef_id in message["HTMLPart"]
    assert "<a href" in message["HTMLPart"]


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
        category=GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
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


def test_for_approval_recipients_for_sensitive_target_close_permission_holders(
    business_area: BusinessArea, close_ticket_role: Role
) -> None:
    closer = UserFactory(email="sensitive-closer@example.com")
    UserRoleAssignmentFactory(user=closer, role=close_ticket_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [closer]


def test_for_approval_recipients_for_complaint_target_close_permission_holders(
    business_area: BusinessArea, close_ticket_role: Role
) -> None:
    closer = UserFactory(email="complaint-closer@example.com")
    UserRoleAssignmentFactory(user=closer, role=close_ticket_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [closer]


def test_for_approval_recipients_for_beneficiary_target_close_permission_holders(
    business_area: BusinessArea, close_ticket_role: Role
) -> None:
    closer = UserFactory(email="beneficiary-closer@example.com")
    UserRoleAssignmentFactory(user=closer, role=close_ticket_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_BENEFICIARY,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [closer]


def test_for_approval_recipients_for_referral_target_feedback_close_permission_holders(
    business_area: BusinessArea, close_feedback_ticket_role: Role, close_ticket_role: Role
) -> None:
    feedback_closer = UserFactory(email="referral-closer@example.com")
    UserRoleAssignmentFactory(user=feedback_closer, role=close_feedback_ticket_role, business_area=business_area)

    excluding_feedback_closer = UserFactory(email="referral-wrong-closer@example.com")
    UserRoleAssignmentFactory(user=excluding_feedback_closer, role=close_ticket_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [feedback_closer]


def test_for_approval_recipients_for_sensitive_exclude_holders_without_close_permission(
    business_area: BusinessArea, sensitive_role: Role
) -> None:
    viewer = UserFactory(email="sensitive-viewer-noclose@example.com")
    UserRoleAssignmentFactory(user=viewer, role=sensitive_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == []


def test_for_approval_recipients_for_sensitive_include_creator_with_as_creator_close_permission(
    business_area: BusinessArea, close_ticket_as_creator_role: Role
) -> None:
    creator = UserFactory(email="sensitive-creator-closer@example.com")
    UserRoleAssignmentFactory(user=creator, role=close_ticket_as_creator_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        created_by=creator,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL)

    assert list(notification.user_recipients) == [creator]


def test_for_approval_recipients_for_sensitive_exclude_editor_who_performed_the_action(
    business_area: BusinessArea, close_ticket_role: Role
) -> None:
    editor = UserFactory(email="sensitive-editor-closer@example.com")
    UserRoleAssignmentFactory(user=editor, role=close_ticket_role, business_area=business_area)
    other_closer = UserFactory(email="sensitive-other-closer@example.com")
    UserRoleAssignmentFactory(user=other_closer, role=close_ticket_role, business_area=business_area)

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        assigned_to=None,
    )

    notification = GrievanceNotification(ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL, editor=editor)

    assert list(notification.user_recipients) == [other_closer]
