from typing import Any
from unittest import mock

from constance.test import override_config
from django.test import override_settings
import pytest

from extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.notifications import PDUOnlineEditNotification
from hope.models import BusinessArea, PDUOnlineEdit, Role, RoleAssignment

pytestmark = pytest.mark.django_db


# ============ Helper Functions ============


def create_user_role_with_permissions(
    user, permissions, business_area, program=None, name=None, whole_business_area_access=False
):
    permission_list = [perm.value for perm in permissions]
    name = name or f"User Role with Permissions {permission_list[0:3]}"
    role, _ = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
    if not program and not whole_business_area_access:
        program = ProgramFactory(business_area=business_area, name="Program for User Role")
    RoleAssignment.objects.get_or_create(user=user, role=role, business_area=business_area, program=program)


def create_partner_role_with_permissions(
    partner, permissions, business_area, program=None, name=None, whole_business_area_access=False
):
    permission_list = [perm.value for perm in permissions]
    name = name or f"Partner Role with Permissions {permission_list[0:3]}"
    role, _ = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
    if not program and not whole_business_area_access:
        program = ProgramFactory(business_area=business_area, name="Program for Partner Role")
    partner.allowed_business_areas.add(business_area)
    RoleAssignment.objects.get_or_create(partner=partner, role=role, business_area=business_area, program=program)


# ============ Fixtures ============


@pytest.fixture
def afghanistan():
    create_afghanistan()
    return BusinessArea.objects.get(slug="afghanistan")


@pytest.fixture
def partner_empty():
    return PartnerFactory(name="Empty Partner")


@pytest.fixture
def program(afghanistan):
    return ProgramFactory(business_area=afghanistan)


@pytest.fixture
def program2(afghanistan):
    return ProgramFactory(business_area=afghanistan)


@pytest.fixture
def user_pdu_creator(partner_empty):
    return UserFactory(partner=partner_empty)


@pytest.fixture
def user_action_user():
    return UserFactory()


@pytest.fixture
def action_permissions_list():
    return [
        Permissions.PDU_ONLINE_SAVE_DATA,
        Permissions.PDU_ONLINE_APPROVE,
        Permissions.PDU_ONLINE_MERGE,
    ]


@pytest.fixture
def pdu_online_edit(afghanistan, program, user_pdu_creator):
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
def partner_unicef_hq():
    partner_unicef = PartnerFactory(name="UNICEF")
    return PartnerFactory(name="UNICEF HQ", parent=partner_unicef)


@pytest.fixture
def partner_unicef_in_ba(afghanistan):
    return PartnerFactory(name=f"UNICEF Partner for {afghanistan.slug}")


@pytest.fixture
def partner_with_action_permissions(afghanistan, program, action_permissions_list):
    partner = PartnerFactory(name="Partner with action permissions")
    create_partner_role_with_permissions(
        partner, action_permissions_list, afghanistan, program=program, name="Role with action permissions"
    )
    return partner


@pytest.fixture
def partner_with_action_permissions_in_whole_ba(afghanistan, action_permissions_list):
    partner = PartnerFactory(name="Partner with action permissions in whole business area")
    create_partner_role_with_permissions(
        partner,
        action_permissions_list,
        afghanistan,
        whole_business_area_access=True,
        name="Role with action permissions",
    )
    return partner


@pytest.fixture
def setup_roles_and_permissions(afghanistan, program, partner_unicef_hq, user_action_user, action_permissions_list):
    """Setup roles and permissions for UNICEF HQ partner."""
    # Create role with action permissions for UNICEF HQ partner
    create_partner_role_with_permissions(
        partner_unicef_hq, action_permissions_list, afghanistan, program=program, name="Role with action permissions"
    )

    # Grant permissions to user performing the action
    create_user_role_with_permissions(
        user_action_user, action_permissions_list, afghanistan, program=program, name="Role with action permissions"
    )

    # Create role for UNICEF Partners
    role_for_unicef_partners = RoleFactory(name="Role for UNICEF Partners")
    role_for_unicef_partners.permissions = [Permissions.PDU_ONLINE_APPROVE.value]
    role_for_unicef_partners.save()


@pytest.fixture
def authorized_users(
    afghanistan,
    program,
    partner_empty,
    partner_unicef_hq,
    partner_unicef_in_ba,
    partner_with_action_permissions,
    partner_with_action_permissions_in_whole_ba,
    action_permissions_list,
    setup_roles_and_permissions,
):
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
        users["edit_authorized"],
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        program=program,
        name="Role with edit permission",
    )
    users["edit_in_ba_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["edit_in_ba_authorized"],
        [Permissions.PDU_ONLINE_SAVE_DATA],
        afghanistan,
        whole_business_area_access=True,
        name="Role with edit permission",
    )

    # Approval permission users
    users["approval_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["approval_authorized"],
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        program=program,
        name="Role with approval permission",
    )
    users["approval_in_ba_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["approval_in_ba_authorized"],
        [Permissions.PDU_ONLINE_APPROVE],
        afghanistan,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    # Merge permission users
    users["merge_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["merge_authorized"],
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program=program,
        name="Role with merge permission",
    )
    users["merge_in_ba_authorized"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["merge_in_ba_authorized"],
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        whole_business_area_access=True,
        name="Role with merge permission",
    )

    return users


@pytest.fixture
def pdu_with_authorized_users(pdu_online_edit, authorized_users):
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


# ============ Tests ============


class TestPDUOnlineEditNotification:
    def test_send_for_approval_action_notification_recipients(
        self, pdu_with_authorized_users, user_action_user, authorized_users
    ) -> None:
        """Test that send for approval action notifies users with approve permission."""
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
        self, pdu_with_authorized_users, user_action_user, authorized_users
    ) -> None:
        """Test that approve action notifies users with merge permission."""
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
        self, pdu_with_authorized_users, user_action_user, authorized_users
    ) -> None:
        """Test that send back action notifies users with save data permission."""
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
        self, afghanistan, program, user_pdu_creator, user_action_user, setup_roles_and_permissions
    ) -> None:
        """Test that when no authorized users are set, no notifications are sent."""
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
    def test_send_email_notification(self, mock_send: Any, pdu_with_authorized_users, user_action_user) -> None:
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
        self, mock_send: Any, pdu_with_authorized_users, user_action_user, afghanistan
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
        self, mock_send: Any, pdu_with_authorized_users, user_action_user, afghanistan
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
        self, mock_send: Any, pdu_with_authorized_users, user_action_user
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
        self, mock_send: Any, pdu_with_authorized_users, user_action_user
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
        self, mock_post: Any, pdu_with_authorized_users, user_action_user
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
        self, mock_post: Any, pdu_with_authorized_users, user_action_user, authorized_users
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
        self, pdu_with_authorized_users, user_action_user, authorized_users
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
        self, mock_send: Any, pdu_with_authorized_users, user_action_user
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
        self, mock_send: Any, pdu_with_authorized_users, user_action_user, afghanistan
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
        self, mock_send: Any, pdu_with_authorized_users, user_action_user, afghanistan
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
        self, pdu_with_authorized_users, user_action_user, user_pdu_creator, program
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
