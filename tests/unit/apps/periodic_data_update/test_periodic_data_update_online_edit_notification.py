from typing import Any
from unittest import mock

from constance.test import override_config
from django.test import override_settings

from extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.base_test_case import BaseTestCase
from hope.apps.core.models import BusinessArea
from hope.apps.periodic_data_update.models import PDUOnlineEdit
from hope.apps.periodic_data_update.notifications import PDUOnlineEditNotification


class TestPDUOnlineEditNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        partner_empty = PartnerFactory(name="Empty Partner")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user_pdu_creator = UserFactory(partner=partner_empty)
        cls.user_action_user = UserFactory()
        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.program2 = ProgramFactory(business_area=cls.business_area)

        # Create PDU Online Edit
        cls.pdu_online_edit = PDUOnlineEditFactory(
            name="Test PDU Edit",
            business_area=cls.business_area,
            program=cls.program,
            created_by=cls.user_pdu_creator,
            status=PDUOnlineEdit.Status.NEW,
            edit_data=[],
            number_of_records=0,
        )

        # potential recipients
        partner_unicef = PartnerFactory(name="UNICEF")
        partner_unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner_unicef)
        partner_unicef_in_ba = PartnerFactory(name=f"UNICEF Partner for {cls.business_area.slug}")

        action_permissions_list = [
            Permissions.PDU_ONLINE_SAVE_DATA,
            Permissions.PDU_ONLINE_APPROVE,
            Permissions.PDU_ONLINE_MERGE,
        ]

        # Adjust Role with all permissions
        role_with_all_permissions = (
            partner_unicef_hq.role_assignments.filter(business_area=cls.business_area).first().role
        )
        role_with_all_permissions.permissions = [perm.value for perm in action_permissions_list]
        role_with_all_permissions.save()

        # grant permissions to user performing the action - action user should be excluded from recipients
        cls.create_user_role_with_permissions(
            cls.user_action_user,
            action_permissions_list,
            cls.business_area,
            program=cls.program,
            name="Role with action permissions",
        )

        # partners setup
        partner_with_different_role_in_program = PartnerFactory(name="Partner with different role in program")
        cls.create_partner_role_with_permissions(
            partner_with_different_role_in_program,
            [Permissions.PROGRAMME_CREATE],
            cls.business_area,
            cls.program,
            name="Role with different permissions",
        )

        partner_with_approval_permission_in_different_program = PartnerFactory(
            name="Partner with approval permission in different program"
        )
        cls.create_partner_role_with_permissions(
            partner_with_approval_permission_in_different_program,
            [Permissions.PDU_ONLINE_APPROVE],
            cls.business_area,
            cls.program2,
            name="Role with approval permission",
        )

        partner_with_action_permissions = PartnerFactory(name="Partner with action permissions")
        cls.create_partner_role_with_permissions(
            partner_with_action_permissions,
            action_permissions_list,
            cls.business_area,
            program=cls.program,
            name="Role with action permissions",
        )

        partner_with_action_permissions_in_whole_ba = PartnerFactory(
            name="Partner with action permissions in whole business area"
        )
        cls.create_partner_role_with_permissions(
            partner_with_action_permissions_in_whole_ba,
            action_permissions_list,
            cls.business_area,
            whole_business_area_access=True,
            name="Role with action permissions",
        )

        # users setup
        cls.user_with_partner_unicef_hq = UserFactory(
            partner=partner_unicef_hq
        )  # UNICEF HQ has "Role with all permissions"
        cls.user_with_partner_unicef_in_ba = UserFactory(partner=partner_unicef_in_ba)  # has "Role for UNICEF Partners"
        cls.user_with_partner_unicef_hq_authorized = UserFactory(
            partner=partner_unicef_hq
        )
        cls.user_with_partner_unicef_in_ba_authorized = UserFactory(partner=partner_unicef_in_ba)


        # adjust "Role for UNICEF Partners" to have only approval permission
        role_for_unicef_partners = RoleFactory(name="Role for UNICEF Partners")
        role_for_unicef_partners.permissions = [Permissions.PDU_ONLINE_APPROVE.value]
        role_for_unicef_partners.save()

        # users with no permissions
        cls.user_with_no_permissions = UserFactory(partner=partner_empty)
        cls.user_with_no_permissions_partner_with_different_role_in_program = UserFactory(
            partner=partner_with_different_role_in_program
        )
        cls.user_with_no_permissions_partner_with_approval_permission_in_different_program = UserFactory(
            partner=partner_with_approval_permission_in_different_program
        )

        # users with partner's permission
        cls.user_with_no_permissions_partner_with_action_permissions = UserFactory(
            partner=partner_with_action_permissions
        )
        cls.user_with_no_permissions_partner_with_action_permissions_authorized = UserFactory(
            partner=partner_with_action_permissions
        )
        cls.user_with_no_permissions_partner_with_action_permissions_in_whole_ba = UserFactory(
            partner=partner_with_action_permissions_in_whole_ba
        )
        cls.user_with_no_permissions_partner_with_action_permissions_in_whole_ba_authorized = UserFactory(
            partner=partner_with_action_permissions_in_whole_ba
        )

        # users with approval permission
        cls.user_with_approval_permission = UserFactory(
            partner=partner_empty
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission,
            [Permissions.PDU_ONLINE_APPROVE],
            cls.business_area,
            program=cls.program,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_authorized = UserFactory(
            partner=partner_empty
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_authorized,
            [Permissions.PDU_ONLINE_APPROVE],
            cls.business_area,
            program=cls.program,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_in_ba = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_in_ba,
            [Permissions.PDU_ONLINE_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_in_ba_authorized = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_in_ba_authorized,
            [Permissions.PDU_ONLINE_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        # users with merge permission
        cls.user_with_merge_permission = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_merge_permission,
            [Permissions.PDU_ONLINE_MERGE],
            cls.business_area,
            program=cls.program,
            name="Role with merge permission",
        )

        cls.user_with_merge_permission_authorized = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_merge_permission_authorized,
            [Permissions.PDU_ONLINE_MERGE],
            cls.business_area,
            program=cls.program,
            name="Role with merge permission",
        )

        cls.user_with_merge_permission_in_ba = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_merge_permission_in_ba,
            [Permissions.PDU_ONLINE_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        cls.user_with_merge_permission_in_ba_authorized = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_merge_permission_in_ba_authorized,
            [Permissions.PDU_ONLINE_MERGE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with merge permission",
        )

        # Add some of these users to authorized_users for the PDU Online Edit
        cls.pdu_online_edit.authorized_users.add(
            cls.user_with_partner_unicef_hq_authorized,
            cls.user_with_partner_unicef_in_ba_authorized,
            cls.user_with_no_permissions_partner_with_action_permissions_authorized,
            cls.user_with_no_permissions_partner_with_action_permissions_in_whole_ba_authorized,
            cls.user_with_approval_permission_authorized,
            cls.user_with_approval_permission_in_ba_authorized,
            cls.user_with_merge_permission_authorized,
            cls.user_with_merge_permission_in_ba_authorized,
        )

    def test_send_for_approval_action_notification_recipients(self) -> None:
        """
        Test that send for approval action notifies users with approve permission
        who are in the authorized users list.
        """
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )

        expected_recipients = [
            self.user_with_partner_unicef_hq_authorized,
            self.user_with_partner_unicef_in_ba_authorized,
            self.user_with_no_permissions_partner_with_action_permissions_authorized,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba_authorized,
            self.user_with_approval_permission_authorized,
            self.user_with_approval_permission_in_ba_authorized,
        ]
        actual_recipients = list(pdu_notification.user_recipients.all())
        assert len(actual_recipients) == len(expected_recipients)
        for expected_recipient in expected_recipients:
            assert expected_recipient in actual_recipients

        assert self.user_action_user not in actual_recipients

    def test_approve_action_notification_recipients(self) -> None:
        """
        Test that approve action notifies users with merge permission
        who are in the authorized users list.
        """
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_APPROVE,
            self.user_action_user,
            "1 January 2025",
        )

        expected_recipients = [
            self.user_with_partner_unicef_hq_authorized,
            self.user_with_no_permissions_partner_with_action_permissions_authorized,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba_authorized,
            self.user_with_merge_permission_authorized,
            self.user_with_merge_permission_in_ba_authorized,
        ]
        actual_recipients = list(pdu_notification.user_recipients.all())
        assert len(actual_recipients) == len(expected_recipients)
        for expected_recipient in expected_recipients:
            assert expected_recipient in actual_recipients

        assert self.user_action_user not in actual_recipients

    def test_send_back_action_notification_recipients(self) -> None:
        """
        Test that send back action notifies the creator of the PDU Edit.
        """
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_BACK,
            self.user_action_user,
            "1 January 2025",
        )

        expected_recipients = [self.user_pdu_creator]
        actual_recipients = list(pdu_notification.user_recipients.all())

        assert len(actual_recipients) == len(expected_recipients)
        assert self.user_pdu_creator in actual_recipients

    def test_no_authorized_users_no_recipients(self) -> None:
        """
        Test that when no authorized users are set, no notifications are sent.
        """
        pdu_edit_no_auth = PDUOnlineEdit.objects.create(
            name="Test PDU Edit No Auth",
            business_area=self.business_area,
            program=self.program,
            created_by=self.user_pdu_creator,
            status=PDUOnlineEdit.Status.NEW,
            edit_data=[],
            number_of_records=0,
        )

        pdu_notification = PDUOnlineEditNotification(
            pdu_edit_no_auth,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )

        actual_recipients = list(pdu_notification.user_recipients.all())
        self.assertEqual(actual_recipients, [])

    @override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
    @mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
    def test_send_email_notification(self, mock_send: Any) -> None:
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )
        pdu_notification.send_email_notification()
        assert mock_send.call_count == 1

    @override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=False)
    @mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
    def test_send_email_notification_disabled_by_config(self, mock_send: Any) -> None:
        self.business_area.enable_email_notification = True
        self.business_area.save()

        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )
        pdu_notification.send_email_notification()
        mock_send.assert_not_called()

    @override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
    @mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
    def test_send_email_notification_disabled_by_business_area(self, mock_send: Any) -> None:
        self.business_area.enable_email_notification = False
        self.business_area.save()

        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )
        pdu_notification.send_email_notification()
        mock_send.assert_not_called()

    @mock.patch("hope.apps.periodic_data_update.notifications.MailjetClient.send_email")
    @override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    def test_send_email_notification_subject_test_env(self, mock_send: Any) -> None:
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )
        assert pdu_notification.email.subject == "[test] PDU Online Edit pending for Approval"

    @mock.patch("hope.apps.periodic_data_update.notifications.MailjetClient.send_email")
    @override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
    @override_settings(EMAIL_SUBJECT_PREFIX="")
    def test_send_email_notification_subject_prod_env(self, mock_send: Any) -> None:
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
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
    def test_send_email_notification_catch_all_email(self, mock_post: Any) -> None:
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
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
    def test_send_email_notification_without_catch_all_email(self, mock_post: Any) -> None:
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )
        pdu_notification.send_email_notification()
        expected_recipients = [
            self.user_with_partner_unicef_hq_authorized,
            self.user_with_partner_unicef_in_ba_authorized,
            self.user_with_no_permissions_partner_with_action_permissions_authorized,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba_authorized,
            self.user_with_approval_permission_authorized,
            self.user_with_approval_permission_in_ba_authorized,
        ]
        actual_recipients = list(pdu_notification.user_recipients.all())
        assert len(actual_recipients) == len(expected_recipients)
        for expected_recipient in expected_recipients:
            assert expected_recipient in actual_recipients

        assert mock_post.call_count == 1

    @override_settings(ENV="prod")
    def send_email_notification_exclude_superuser(self) -> None:
        self.user_with_partner_unicef_hq.is_superuser = True
        self.user_with_partner_unicef_hq.save()

        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )

        actual_recipients = list(pdu_notification.user_recipients.all())
        assert len(actual_recipients) == 5
        assert self.user_with_partner_unicef_hq not in actual_recipients

    @override_config(
        SEND_PDU_ONLINE_EDIT_NOTIFICATION=True,
        MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION=123456,
    )
    @mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
    def test_email_body_variables_send_for_approval(self, mock_send: Any) -> None:
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
            "1 January 2025",
        )
        pdu_notification.send_email_notification()
        assert mock_send.call_count == 1

        self.assertEqual(pdu_notification.email_subject, "PDU Online Edit pending for Approval")
        self.assertEqual(pdu_notification.action_name, "sent for approval")
        self.assertEqual(pdu_notification.recipient_title, "Approver")

    @override_config(
        SEND_PDU_ONLINE_EDIT_NOTIFICATION=True,
        MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION=123456,
    )
    @mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
    def test_email_body_variables_approve(self, mock_send: Any) -> None:
        self.business_area.enable_email_notification = True
        self.business_area.save()

        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_APPROVE,
            self.user_action_user,
            "1 January 2025",
        )
        pdu_notification.send_email_notification()
        assert mock_send.call_count == 1

        self.assertEqual(pdu_notification.email_subject, "PDU Online Edit pending for Merge")
        self.assertEqual(pdu_notification.action_name, "approved")
        self.assertEqual(pdu_notification.recipient_title, "Merger")

    @override_config(
        SEND_PDU_ONLINE_EDIT_NOTIFICATION=True,
        MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION=123456,
    )
    @mock.patch("hope.apps.utils.mailjet.MailjetClient.send_email")
    def test_email_body_variables_send_back(self, mock_send: Any) -> None:
        self.business_area.enable_email_notification = True
        self.business_area.save()

        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_BACK,
            self.user_action_user,
            "1 January 2025",
        )
        pdu_notification.send_email_notification()
        assert mock_send.call_count == 1

        self.assertEqual(pdu_notification.email_subject, "PDU Online Edit sent back")
        self.assertEqual(pdu_notification.action_name, "sent back")
        self.assertEqual(pdu_notification.recipient_title, "Creator")

    def test_email_body_variables_content(self) -> None:
        pdu_notification = PDUOnlineEditNotification(
            self.pdu_online_edit,
            PDUOnlineEditNotification.ACTION_SEND_FOR_APPROVAL,
            self.user_action_user,
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
            self.assertIn(key, body_variables)

        assert body_variables["first_name"] == "PDU Online Edit"
        assert body_variables["last_name"] == "Approver"
        assert body_variables["action_name"] == "sent for approval"
        assert body_variables["pdu_online_edit_id"] == self.pdu_online_edit.id
        assert body_variables["pdu_online_edit_name"] == "Test PDU Edit"
        assert body_variables["pdu_creator"] == self.user_pdu_creator.get_full_name()
        assert body_variables["pdu_creation_date"] == f"{self.pdu_online_edit.created_at:%-d %B %Y}"
        assert body_variables["action_user"] == self.user_action_user.get_full_name()
        assert body_variables["action_date"] == "1 January 2025"
        assert body_variables["program_name"] == self.program.name
        assert f"/population/individuals/online-templates/{self.pdu_online_edit.id}" in body_variables["pdu_online_edit_url"]
