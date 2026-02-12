"""Tests for PDU online edit notifications."""

from typing import Any
from unittest import mock

from constance.test import override_config
from django.test import override_settings
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    PDUOnlineEditFactory,
    ProgramFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.notifications import PDUOnlineEditNotification
from hope.models import BusinessArea, PDUOnlineEdit, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def partner_empty(db: Any) -> Any:
    return PartnerFactory(name="Empty Partner")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Any:
    return ProgramFactory(business_area=afghanistan)


@pytest.fixture
def program2(afghanistan: BusinessArea) -> Any:
    return ProgramFactory(business_area=afghanistan)


@pytest.fixture
def user_pdu_creator(partner_empty: Any) -> User:
    return UserFactory(partner=partner_empty)


@pytest.fixture
def user_action_user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def action_permissions_list() -> list:
    return [
        Permissions.PDU_ONLINE_SAVE_DATA,
        Permissions.PDU_ONLINE_APPROVE,
        Permissions.PDU_ONLINE_MERGE,
    ]


@pytest.fixture
def pdu_online_edit(afghanistan: BusinessArea, program: Any, user_pdu_creator: User) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        name="Test PDU Edit",
        business_area=afghanistan,
        program=program,
        created_by=user_pdu_creator,
        status=PDUOnlineEdit.Status.NEW,
        edit_data=[],
        number_of_records=0,
    )


@pytest.fixture
def partner_unicef_hq(db: Any) -> Any:
    partner_unicef = PartnerFactory(name="UNICEF")
    return PartnerFactory(name="UNICEF HQ", parent=partner_unicef)


@pytest.fixture
def partner_unicef_in_ba(afghanistan: BusinessArea) -> Any:
    return PartnerFactory(name=f"UNICEF Partner for {afghanistan.slug}")


@pytest.fixture
def partner_with_action_permissions(
    afghanistan: BusinessArea,
    program: Any,
    action_permissions_list: list,
    create_partner_role_with_permissions: Any,
) -> Any:
    partner = PartnerFactory(name="Partner with action permissions")
    create_partner_role_with_permissions(
        partner=partner,
        permissions=action_permissions_list,
        business_area=afghanistan,
        program=program,
    )
    return partner


@pytest.fixture
def partner_with_action_permissions_in_whole_ba(
    afghanistan: BusinessArea,
    action_permissions_list: list,
    create_partner_role_with_permissions: Any,
) -> Any:
    partner = PartnerFactory(name="Partner with action permissions in whole business area")
    create_partner_role_with_permissions(
        partner=partner,
        permissions=action_permissions_list,
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    return partner


@pytest.fixture
def setup_roles_and_permissions(
    afghanistan: BusinessArea,
    program: Any,
    partner_unicef_hq: Any,
    user_action_user: User,
    action_permissions_list: list,
    create_partner_role_with_permissions: Any,
    create_user_role_with_permissions: Any,
) -> None:
    """Setup roles and permissions for UNICEF HQ partner."""
    # Create role with action permissions for UNICEF HQ partner
    create_partner_role_with_permissions(
        partner=partner_unicef_hq,
        permissions=action_permissions_list,
        business_area=afghanistan,
        program=program,
    )

    # Grant permissions to user performing the action
    create_user_role_with_permissions(
        user=user_action_user,
        permissions=action_permissions_list,
        business_area=afghanistan,
        program=program,
    )

    # Create role for UNICEF Partners
    role_for_unicef_partners = RoleFactory(name="Role for UNICEF Partners")
    role_for_unicef_partners.permissions = [Permissions.PDU_ONLINE_APPROVE.value]
    role_for_unicef_partners.save()


@pytest.fixture
def authorized_users(
    afghanistan: BusinessArea,
    program: Any,
    partner_empty: Any,
    partner_unicef_hq: Any,
    partner_unicef_in_ba: Any,
    partner_with_action_permissions: Any,
    partner_with_action_permissions_in_whole_ba: Any,
    setup_roles_and_permissions: None,
    create_user_role_with_permissions: Any,
) -> dict:
    """Create all authorized users."""
    users = {}

    # UNICEF users
    users["unicef_hq_authorized"] = UserFactory(partner=partner_unicef_hq)
    users["unicef_in_ba_authorized"] = UserFactory(partner=partner_unicef_in_ba)

    # Partner users
    users["partner_action_authorized"] = UserFactory(partner=partner_with_action_permissions)
    users["partner_action_whole_ba_authorized"] = UserFactory(partner=partner_with_action_permissions_in_whole_ba)

    # Edit permission users
    users["edit_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        user=users["edit_authorized"],
        permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
        business_area=afghanistan,
        program=program,
    )
    users["edit_in_ba_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        user=users["edit_in_ba_authorized"],
        permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    # Approval permission users
    users["approval_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        user=users["approval_authorized"],
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=afghanistan,
        program=program,
    )
    users["approval_in_ba_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        user=users["approval_in_ba_authorized"],
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    # Merge permission users
    users["merge_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        user=users["merge_authorized"],
        permissions=[Permissions.PDU_ONLINE_MERGE],
        business_area=afghanistan,
        program=program,
    )
    users["merge_in_ba_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        user=users["merge_in_ba_authorized"],
        permissions=[Permissions.PDU_ONLINE_MERGE],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    return users


@pytest.fixture
def pdu_with_authorized_users(pdu_online_edit: PDUOnlineEdit, authorized_users: dict) -> PDUOnlineEdit:
    """Add authorized users to PDU Online Edit."""
    pdu_online_edit.authorized_users.add(
        authorized_users["unicef_hq_authorized"],
        authorized_users["unicef_in_ba_authorized"],
        authorized_users["partner_action_authorized"],
        authorized_users["partner_action_whole_ba_authorized"],
        authorized_users["edit_authorized"],
        authorized_users["edit_in_ba_authorized"],
        authorized_users["approval_authorized"],
        authorized_users["approval_in_ba_authorized"],
        authorized_users["merge_authorized"],
        authorized_users["merge_in_ba_authorized"],
    )
    return pdu_online_edit


def test_send_for_approval_action_notification_recipients(
    pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, authorized_users: dict
) -> None:
    # Send for approval action notifies users with approve permission.
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )

    expected_recipients = [
        authorized_users["unicef_hq_authorized"],
        authorized_users["unicef_in_ba_authorized"],
        authorized_users["partner_action_authorized"],
        authorized_users["partner_action_whole_ba_authorized"],
        authorized_users["approval_authorized"],
        authorized_users["approval_in_ba_authorized"],
    ]
    actual_recipients = list(pdu_notification.user_recipients.all())
    assert len(actual_recipients) == len(expected_recipients)
    for expected_recipient in expected_recipients:
        assert expected_recipient in actual_recipients

    assert user_action_user not in actual_recipients


def test_approve_action_notification_recipients(
    pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, authorized_users: dict
) -> None:
    # Approve action notifies users with merge permission.
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_APPROVE,
        user_action_user,
        "1 January 2025",
    )

    expected_recipients = [
        authorized_users["unicef_hq_authorized"],
        authorized_users["partner_action_authorized"],
        authorized_users["partner_action_whole_ba_authorized"],
        authorized_users["merge_authorized"],
        authorized_users["merge_in_ba_authorized"],
    ]
    actual_recipients = list(pdu_notification.user_recipients.all())
    assert len(actual_recipients) == len(expected_recipients)
    for expected_recipient in expected_recipients:
        assert expected_recipient in actual_recipients

    assert user_action_user not in actual_recipients


def test_send_back_action_notification_recipients(
    pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, authorized_users: dict
) -> None:
    # Send back action notifies users with save data permission.
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_BACK,
        user_action_user,
        "1 January 2025",
    )

    expected_recipients = [
        authorized_users["unicef_hq_authorized"],
        authorized_users["partner_action_authorized"],
        authorized_users["partner_action_whole_ba_authorized"],
        authorized_users["edit_authorized"],
        authorized_users["edit_in_ba_authorized"],
    ]
    actual_recipients = list(pdu_notification.user_recipients.all())
    assert len(actual_recipients) == len(expected_recipients)
    for expected_recipient in expected_recipients:
        assert expected_recipient in actual_recipients


def test_no_authorized_users_no_recipients(
    afghanistan: BusinessArea,
    program: Any,
    user_pdu_creator: User,
    user_action_user: User,
    setup_roles_and_permissions: None,
) -> None:
    # When no authorized users are set, no notifications are sent.
    pdu_edit_no_auth = PDUOnlineEdit.objects.create(
        name="Test PDU Edit No Auth",
        business_area=afghanistan,
        program=program,
        created_by=user_pdu_creator,
        status=PDUOnlineEdit.Status.NEW,
        edit_data=[],
        number_of_records=0,
    )

    pdu_notification = PDUOnlineEditNotification(
        pdu_edit_no_auth,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )

    actual_recipients = list(pdu_notification.user_recipients.all())
    assert actual_recipients == []


@override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
@mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
def test_send_email_notification(
    mock_send: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User
) -> None:
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )
    pdu_notification.send_email_notification()
    assert mock_send.call_count == 1


@override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=False)
@mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
def test_send_email_notification_disabled_by_config(
    mock_send: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, afghanistan: BusinessArea
) -> None:
    afghanistan.enable_email_notification = True
    afghanistan.save()

    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )
    pdu_notification.send_email_notification()
    mock_send.assert_not_called()


@override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
@mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
def test_send_email_notification_disabled_by_business_area(
    mock_send: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, afghanistan: BusinessArea
) -> None:
    afghanistan.enable_email_notification = False
    afghanistan.save()

    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )
    pdu_notification.send_email_notification()
    mock_send.assert_not_called()


@mock.patch("hope.apps.periodic_data_update.notifications.MailjetClient.send_email")
@override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
@override_settings(EMAIL_SUBJECT_PREFIX="test")
def test_send_email_notification_subject_test_env(
    mock_send: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User
) -> None:
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )
    assert pdu_notification.email.subject == "[test] PDU Online Edit pending for Approval"


@mock.patch("hope.apps.periodic_data_update.notifications.MailjetClient.send_email")
@override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
@override_settings(EMAIL_SUBJECT_PREFIX="")
def test_send_email_notification_subject_prod_env(
    mock_send: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User
) -> None:
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )
    assert pdu_notification.email.subject == "PDU Online Edit pending for Approval"


@mock.patch("hope.apps.utils.celery_tasks.requests.post")
@override_config(
    SEND_PDU_ONLINE_EDIT_NOTIFICATION=True,
    ENABLE_MAILJET=True,
    MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION=1,
)
@override_settings(CATCH_ALL_EMAIL=["catchallemail@email.com", "catchallemail2@email.com"])
def test_send_email_notification_catch_all_email(
    mock_post: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User
) -> None:
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )
    pdu_notification.send_email_notification()
    assert len(pdu_notification.email.recipients) == 2
    assert "catchallemail@email.com" in pdu_notification.email.recipients
    assert "catchallemail2@email.com" in pdu_notification.email.recipients
    assert mock_post.call_count == 1


@mock.patch("hope.apps.utils.celery_tasks.requests.post")
@override_config(
    SEND_PDU_ONLINE_EDIT_NOTIFICATION=True,
    ENABLE_MAILJET=True,
    MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION=1,
)
def test_send_email_notification_without_catch_all_email(
    mock_post: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, authorized_users: dict
) -> None:
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )
    pdu_notification.send_email_notification()
    expected_recipients = [
        authorized_users["unicef_hq_authorized"],
        authorized_users["unicef_in_ba_authorized"],
        authorized_users["partner_action_authorized"],
        authorized_users["partner_action_whole_ba_authorized"],
        authorized_users["approval_authorized"],
        authorized_users["approval_in_ba_authorized"],
    ]
    actual_recipients = list(pdu_notification.user_recipients.all())
    assert len(actual_recipients) == len(expected_recipients)
    for expected_recipient in expected_recipients:
        assert expected_recipient in actual_recipients

    assert mock_post.call_count == 1


@override_settings(ENV="prod")
def send_email_notification_exclude_superuser(
    pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, authorized_users: dict
) -> None:
    # Note: Missing test_ prefix - not run (same as original)
    authorized_users["unicef_hq_authorized"].is_superuser = True
    authorized_users["unicef_hq_authorized"].save()

    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )

    actual_recipients = list(pdu_notification.user_recipients.all())
    assert len(actual_recipients) == 5
    assert authorized_users["unicef_hq_authorized"] not in actual_recipients


@override_config(
    SEND_PDU_ONLINE_EDIT_NOTIFICATION=True,
    MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION=123456,
)
@mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
def test_email_body_variables_send_for_approval(
    mock_send: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User
) -> None:
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )
    pdu_notification.send_email_notification()
    assert mock_send.call_count == 1

    assert pdu_notification.email_subject == "PDU Online Edit pending for Approval"
    assert pdu_notification.action_name == "sent for approval"
    assert pdu_notification.recipient_title == "Approver"


@override_config(
    SEND_PDU_ONLINE_EDIT_NOTIFICATION=True,
    MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION=123456,
)
@mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
def test_email_body_variables_approve(
    mock_send: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, afghanistan: BusinessArea
) -> None:
    afghanistan.enable_email_notification = True
    afghanistan.save()

    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_APPROVE,
        user_action_user,
        "1 January 2025",
    )
    pdu_notification.send_email_notification()
    assert mock_send.call_count == 1

    assert pdu_notification.email_subject == "PDU Online Edit pending for Merge"
    assert pdu_notification.action_name == "approved"
    assert pdu_notification.recipient_title == "Merger"


@override_config(
    SEND_PDU_ONLINE_EDIT_NOTIFICATION=True,
    MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION=123456,
)
@mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
def test_email_body_variables_send_back(
    mock_send: Any, pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, afghanistan: BusinessArea
) -> None:
    afghanistan.enable_email_notification = True
    afghanistan.save()

    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_BACK,
        user_action_user,
        "1 January 2025",
    )
    pdu_notification.send_email_notification()
    assert mock_send.call_count == 1

    assert pdu_notification.email_subject == "PDU Online Edit sent back"
    assert pdu_notification.action_name == "sent back"
    assert pdu_notification.recipient_title == "Editor"


def test_email_body_variables_content(
    pdu_with_authorized_users: PDUOnlineEdit, user_action_user: User, user_pdu_creator: User, program: Any
) -> None:
    pdu_notification = PDUOnlineEditNotification(
        pdu_with_authorized_users,
        PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
        user_action_user,
        "1 January 2025",
    )

    body_variables = pdu_notification._prepare_body_variables()

    expected_keys = [
        "first_name",
        "last_name",
        "action_name",
        "pdu_online_edit_url",
        "pdu_online_edit_id",
        "pdu_online_edit_name",
        "pdu_creator",
        "pdu_creation_date",
        "action_user",
        "action_date",
        "program_name",
    ]

    for key in expected_keys:
        assert key in body_variables

    assert body_variables["first_name"] == "PDU Online Edit"
    assert body_variables["last_name"] == "Approver"
    assert body_variables["action_name"] == "sent for approval"
    assert body_variables["pdu_online_edit_id"] == pdu_with_authorized_users.id
    assert body_variables["pdu_online_edit_name"] == "Test PDU Edit"
    assert body_variables["pdu_creator"] == user_pdu_creator.get_full_name()
    assert body_variables["pdu_creation_date"] == f"{pdu_with_authorized_users.created_at:%-d %B %Y}"
    assert body_variables["action_user"] == user_action_user.get_full_name()
    assert body_variables["action_date"] == "1 January 2025"
    assert body_variables["program_name"] == program.name
    assert (
        f"/population/individuals/online-templates/{pdu_with_authorized_users.id}"
        in body_variables["pdu_online_edit_url"]
    )
