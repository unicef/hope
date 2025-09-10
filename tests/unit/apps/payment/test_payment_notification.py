from typing import Any
from unittest import mock

from constance.test import override_config
from django.test import override_settings
from django.utils import timezone

from extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    PaymentPlanFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.base_test_case import BaseTestCase
from hope.apps.core.models import BusinessArea
from hope.apps.payment.models import Approval, PaymentPlan
from hope.apps.payment.notifications import PaymentNotification


class TestPaymentNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        partner_empty = PartnerFactory(name="Empty Partner")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user_payment_plan_creator = UserFactory(partner=partner_empty)
        cls.user_action_user = UserFactory()
        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.program2 = ProgramFactory(business_area=cls.business_area)
        cls.payment_plan = PaymentPlanFactory(
            business_area=cls.business_area,
            created_by=cls.user_payment_plan_creator,
            program_cycle=cls.program.cycles.first(),
        )

        cls.approval_process = ApprovalProcessFactory(
            payment_plan=cls.payment_plan,
            sent_for_approval_by=cls.user_action_user,
            sent_for_approval_date=timezone.now(),
        )
        cls.approval_approval = ApprovalFactory(
            approval_process=cls.approval_process,
            type=Approval.APPROVAL,
            created_by=cls.user_action_user,
        )
        cls.approval_authorization = ApprovalFactory(
            approval_process=cls.approval_process,
            type=Approval.AUTHORIZATION,
            created_by=cls.user_action_user,
        )
        cls.approval_release = ApprovalFactory(
            approval_process=cls.approval_process,
            type=Approval.FINANCE_RELEASE,
            created_by=cls.user_action_user,
        )

        # potential recipients
        partner_unicef = PartnerFactory(name="UNICEF")
        partner_unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner_unicef)
        partner_unicef_in_ba = PartnerFactory(name=f"UNICEF Partner for {cls.business_area.slug}")

        action_permissions_list = [
            Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
            Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            Permissions.PM_DOWNLOAD_XLSX_FOR_FSP,
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
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
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

        # adjust "Role for UNICEF Partners" to have only approval permission
        role_for_unicef_partners = RoleFactory(name="Role for UNICEF Partners")
        role_for_unicef_partners.permissions = [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.value]
        role_for_unicef_partners.save()

        # no permissions on user combinations
        cls.user_with_no_permissions = UserFactory(partner=partner_empty)
        cls.user_with_no_permissions_partner_with_different_role_in_program = UserFactory(
            partner=partner_with_different_role_in_program
        )
        cls.user_with_no_permissions_partner_with_approval_permission_in_different_program = UserFactory(
            partner=partner_with_approval_permission_in_different_program
        )
        cls.user_with_no_permissions_partner_with_action_permissions = UserFactory(
            partner=partner_with_action_permissions
        )
        cls.user_with_no_permissions_partner_with_action_permissions_in_whole_ba = UserFactory(
            partner=partner_with_action_permissions_in_whole_ba
        )

        # user with approval permission - in program
        cls.user_with_approval_permission_partner_unicef_in_ba = UserFactory(partner=partner_unicef_in_ba)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_unicef_in_ba,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_partner_with_different_role_in_program = UserFactory(
            partner=partner_with_different_role_in_program
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_with_different_role_in_program,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_partner_with_approval_permission_in_different_program = UserFactory(
            partner=partner_with_approval_permission_in_different_program
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_with_approval_permission_in_different_program,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_partner_with_action_permissions = UserFactory(
            partner=partner_with_action_permissions
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_with_action_permissions,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_partner_with_action_permissions_in_whole_ba = UserFactory(
            partner=partner_with_action_permissions_in_whole_ba
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_with_action_permissions_in_whole_ba,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_partner_empty = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_empty,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program,
            name="Role with approval permission",
        )

        # user with approval permission - whole BA
        cls.user_with_approval_permission_in_ba_partner_unicef_in_ba = UserFactory(partner=partner_unicef_in_ba)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_in_ba_partner_unicef_in_ba,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_in_ba_partner_with_different_role_in_program = UserFactory(
            partner=partner_with_different_role_in_program
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_in_ba_partner_with_different_role_in_program,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program = UserFactory(
            partner=partner_with_approval_permission_in_different_program
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_in_ba_partner_with_action_permissions = UserFactory(
            partner=partner_with_action_permissions
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_in_ba_partner_with_action_permissions,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba = UserFactory(
            partner=partner_with_action_permissions_in_whole_ba
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_in_ba_partner_empty = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_in_ba_partner_empty,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with approval permission",
        )

        # user with approval permission - in incorrect program
        cls.user_with_approval_permission_wrong_program_partner_unicef_in_ba = UserFactory(partner=partner_unicef_in_ba)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_wrong_program_partner_unicef_in_ba,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program2,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_wrong_program_partner_with_different_role_in_program = UserFactory(
            partner=partner_with_different_role_in_program
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_wrong_program_partner_with_different_role_in_program,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program2,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program = (
            UserFactory(partner=partner_with_approval_permission_in_different_program)
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program2,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_wrong_program_partner_with_action_permissions = UserFactory(
            partner=partner_with_action_permissions
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_wrong_program_partner_with_action_permissions,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program2,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba = UserFactory(
            partner=partner_with_action_permissions_in_whole_ba
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program2,
            name="Role with approval permission",
        )

        cls.user_with_approval_permission_wrong_program_partner_empty = UserFactory(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_wrong_program_partner_empty,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            program=cls.program2,
            name="Role with approval permission",
        )

        # other action permissions
        cls.user_with_authorize_permission = UserFactory.create(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_authorize_permission,
            [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with authorize permission",
        )
        cls.user_with_review_permission = UserFactory.create(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_review_permission,
            [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with review permission",
        )
        cls.user_with_download_xlsx_permission = UserFactory.create(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_download_xlsx_permission,
            [Permissions.PM_DOWNLOAD_XLSX_FOR_FSP],
            cls.business_area,
            whole_business_area_access=True,
            name="Role with download xlsx permission",
        )

        cls.user_with_action_permissions = UserFactory.create(partner=partner_empty)
        cls.create_user_role_with_permissions(
            cls.user_with_action_permissions,
            action_permissions_list,
            cls.business_area,
            whole_business_area_access=True,
            name="Role with action permissions",
        )

    def test_prepare_user_recipients_for_send_for_approval(self) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )

        assert payment_notification.user_recipients.count() == 20

        for recipient in [
            self.user_with_partner_unicef_hq,
            self.user_with_partner_unicef_in_ba,
            # users with approval permissions
            self.user_with_approval_permission_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_with_different_role_in_program,
            self.user_with_approval_permission_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_partner_with_action_permissions,
            self.user_with_approval_permission_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_partner_empty,
            # users with approval permissions in BA
            self.user_with_approval_permission_in_ba_partner_unicef_in_ba,
            self.user_with_approval_permission_in_ba_partner_with_different_role_in_program,
            self.user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_in_ba_partner_empty,
            # users with incorrect permissions but role from partner
            self.user_with_approval_permission_wrong_program_partner_unicef_in_ba,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba,
            self.user_with_action_permissions,
            # users with no permissions but role from partner
            self.user_with_no_permissions_partner_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba,
        ]:
            assert recipient in payment_notification.user_recipients.all()

        # action user should be excluded from recipients
        assert self.user_action_user not in payment_notification.user_recipients.all()

        for not_recipient in [
            self.user_with_no_permissions,
            self.user_with_no_permissions_partner_with_different_role_in_program,
            self.user_with_no_permissions_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_wrong_program_partner_with_different_role_in_program,
            self.user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_wrong_program_partner_empty,
            self.user_with_authorize_permission,
            self.user_with_review_permission,
            self.user_with_download_xlsx_permission,
        ]:
            assert not_recipient not in payment_notification.user_recipients.all()

    def test_prepare_user_recipients_for_approve(self) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.APPROVE.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        assert payment_notification.user_recipients.count() == 11
        for recipient in [
            self.user_with_authorize_permission,
            self.user_with_partner_unicef_hq,
            self.user_with_approval_permission_partner_with_action_permissions,
            self.user_with_approval_permission_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba,
            self.user_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba,
        ]:
            assert recipient in payment_notification.user_recipients.all()

        # action user should be excluded from recipients
        assert self.user_action_user not in payment_notification.user_recipients.all()

        for not_recipient in [
            self.user_with_no_permissions,
            self.user_with_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_with_different_role_in_program,
            self.user_with_approval_permission_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_partner_empty,
            self.user_with_approval_permission_in_ba_partner_unicef_in_ba,
            self.user_with_approval_permission_in_ba_partner_with_different_role_in_program,
            self.user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_in_ba_partner_empty,
            self.user_with_approval_permission_wrong_program_partner_unicef_in_ba,
            self.user_with_no_permissions_partner_with_different_role_in_program,
            self.user_with_no_permissions_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_wrong_program_partner_with_different_role_in_program,
            self.user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_wrong_program_partner_empty,
            self.user_with_review_permission,
            self.user_with_download_xlsx_permission,
        ]:
            assert not_recipient not in payment_notification.user_recipients.all()

    def test_prepare_user_recipients_for_authorize(self) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.AUTHORIZE.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        assert payment_notification.user_recipients.count() == 11
        for recipient in [
            self.user_with_review_permission,
            self.user_with_partner_unicef_hq,
            self.user_with_approval_permission_partner_with_action_permissions,
            self.user_with_approval_permission_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba,
            self.user_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba,
        ]:
            assert recipient in payment_notification.user_recipients.all()

        # action user should be excluded from recipients
        assert self.user_action_user not in payment_notification.user_recipients.all()

        for not_recipient in [
            self.user_with_no_permissions,
            self.user_with_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_with_different_role_in_program,
            self.user_with_approval_permission_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_partner_empty,
            self.user_with_approval_permission_in_ba_partner_unicef_in_ba,
            self.user_with_approval_permission_in_ba_partner_with_different_role_in_program,
            self.user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_in_ba_partner_empty,
            self.user_with_approval_permission_wrong_program_partner_unicef_in_ba,
            self.user_with_no_permissions_partner_with_different_role_in_program,
            self.user_with_no_permissions_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_wrong_program_partner_with_different_role_in_program,
            self.user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_wrong_program_partner_empty,
            self.user_with_authorize_permission,
            self.user_with_download_xlsx_permission,
        ]:
            assert not_recipient not in payment_notification.user_recipients.all()

    def test_prepare_user_recipients_for_release(self) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.REVIEW.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        assert payment_notification.user_recipients.count() == 11
        for recipient in [
            self.user_with_download_xlsx_permission,
            self.user_with_partner_unicef_hq,
            self.user_with_approval_permission_partner_with_action_permissions,
            self.user_with_approval_permission_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba,
            self.user_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba,
        ]:
            assert recipient in payment_notification.user_recipients.all()

        # action user should be excluded from recipients
        assert self.user_action_user not in payment_notification.user_recipients.all()

        for not_recipient in [
            self.user_with_no_permissions,
            self.user_with_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_with_different_role_in_program,
            self.user_with_approval_permission_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_partner_empty,
            self.user_with_approval_permission_in_ba_partner_unicef_in_ba,
            self.user_with_approval_permission_in_ba_partner_with_different_role_in_program,
            self.user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_in_ba_partner_empty,
            self.user_with_approval_permission_wrong_program_partner_unicef_in_ba,
            self.user_with_no_permissions_partner_with_different_role_in_program,
            self.user_with_no_permissions_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_wrong_program_partner_with_different_role_in_program,
            self.user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_wrong_program_partner_empty,
            self.user_with_authorize_permission,
            self.user_with_review_permission,
        ]:
            assert not_recipient not in payment_notification.user_recipients.all()

    @mock.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    @override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
    def test_send_email_notification(self, mock_send: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        payment_notification.send_email_notification()
        assert mock_send.call_count == 1

    @mock.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    @override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    def test_send_email_notification_subject_test_env(self, mock_send: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        assert payment_notification.email.subject == "[test] Payment pending for Approval"

    @mock.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    @override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
    @override_settings(EMAIL_SUBJECT_PREFIX="")
    def test_send_email_notification_subject_prod_env(self, mock_send: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        assert payment_notification.email.subject == "Payment pending for Approval"

    @mock.patch("hope.apps.utils.celery_tasks.requests.post")
    @override_config(
        SEND_PAYMENT_PLANS_NOTIFICATION=True,
        ENABLE_MAILJET=True,
        MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
    )
    @override_settings(CATCH_ALL_EMAIL=["catchallemail@email.com", "catchallemail2@email.com"])
    def test_send_email_notification_catch_all_email(self, mock_post: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        payment_notification.send_email_notification()
        assert len(payment_notification.email.recipients) == 2
        assert "catchallemail@email.com" in payment_notification.email.recipients
        assert "catchallemail2@email.com" in payment_notification.email.recipients
        assert mock_post.call_count == 1

    @mock.patch("hope.apps.utils.celery_tasks.requests.post")
    @override_config(
        SEND_PAYMENT_PLANS_NOTIFICATION=True,
        ENABLE_MAILJET=True,
        MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
    )
    def test_send_email_notification_without_catch_all_email(self, mock_post: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        payment_notification.send_email_notification()
        assert len(payment_notification.email.recipients) == 20
        for recipient in [
            self.user_with_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_with_different_role_in_program,
            self.user_with_approval_permission_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_partner_with_action_permissions,
            self.user_with_approval_permission_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_partner_empty,
            self.user_with_approval_permission_in_ba_partner_unicef_in_ba,
            self.user_with_approval_permission_in_ba_partner_with_different_role_in_program,
            self.user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_in_ba_partner_empty,
            self.user_with_approval_permission_wrong_program_partner_unicef_in_ba,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba,
            self.user_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba,
        ]:
            assert recipient.email in payment_notification.email.recipients

        assert mock_post.call_count == 1

    @mock.patch("hope.apps.utils.celery_tasks.requests.post")
    @override_config(
        SEND_PAYMENT_PLANS_NOTIFICATION=True,
        ENABLE_MAILJET=True,
        MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
    )
    @override_settings(ENV="prod")
    def test_send_email_notification_exclude_superuser(self, mock_post: Any) -> None:
        self.user_with_partner_unicef_hq.is_superuser = True
        self.user_with_partner_unicef_hq.save()
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        payment_notification.send_email_notification()
        assert len(payment_notification.email.recipients) == 19
        assert self.user_with_partner_unicef_hq.email not in payment_notification.email.recipients

        for recipient in [
            self.user_with_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_unicef_in_ba,
            self.user_with_approval_permission_partner_with_different_role_in_program,
            self.user_with_approval_permission_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_partner_with_action_permissions,
            self.user_with_approval_permission_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_partner_empty,
            self.user_with_approval_permission_in_ba_partner_unicef_in_ba,
            self.user_with_approval_permission_in_ba_partner_with_different_role_in_program,
            self.user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions,
            self.user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba,
            self.user_with_approval_permission_in_ba_partner_empty,
            self.user_with_approval_permission_wrong_program_partner_unicef_in_ba,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions,
            self.user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba,
            self.user_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions,
            self.user_with_no_permissions_partner_with_action_permissions_in_whole_ba,
        ]:
            assert recipient.email in payment_notification.email.recipients

        assert mock_post.call_count == 1
