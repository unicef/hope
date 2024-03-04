from typing import Any
from unittest import mock

from django.utils import timezone

from constance.test import override_config

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Role
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import (
    ApprovalFactory,
    ApprovalProcessFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import Approval, PaymentPlan
from hct_mis_api.apps.payment.notifications import PaymentNotification
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestPaymentNotification(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user_payment_plan_creator = UserFactory.create()
        cls.user_action_user = UserFactory.create()
        cls.program = ProgramFactory.create(business_area=cls.business_area)
        cls.program2 = ProgramFactory.create(business_area=cls.business_area)
        cls.payment_plan = PaymentPlanFactory.create(
            business_area=cls.business_area, created_by=cls.user_payment_plan_creator, program=cls.program
        )

        cls.approval_process = ApprovalProcessFactory.create(
            payment_plan=cls.payment_plan,
            sent_for_approval_by=cls.user_action_user,
            sent_for_approval_date=timezone.now(),
        )
        cls.approval_approval = ApprovalFactory.create(
            approval_process=cls.approval_process,
            type=Approval.APPROVAL,
            created_by=cls.user_action_user,
        )
        cls.approval_authorization = ApprovalFactory.create(
            approval_process=cls.approval_process,
            type=Approval.AUTHORIZATION,
            created_by=cls.user_action_user,
        )
        cls.approval_release = ApprovalFactory.create(
            approval_process=cls.approval_process,
            type=Approval.FINANCE_RELEASE,
            created_by=cls.user_action_user,
        )

        # potential recipients
        partner_unicef = PartnerFactory.create(name="UNICEF")
        partner_with_program_access = PartnerFactory.create(name="Partner with program access")
        partner_with_program_access.permissions = {
            str(cls.business_area.id): {
                "programs": {str(cls.program.id): []},
                "roles": [],
            }
        }
        partner_with_program_access.save()
        partner_without_program_access = PartnerFactory.create(name="Partner without program access")
        partner_without_program_access.permissions = {
            str(cls.business_area.id): {
                "programs": {str(cls.program2.id): []},
                "roles": [],
            }
        }
        partner_without_program_access.save()
        # users with action permissions
        cls.user_with_approval_permission_partner_unicef = UserFactory.create(partner=partner_unicef)
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_unicef,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            name="Role with approval permission",
        )
        cls.user_with_approval_permission_partner_with_program_access = UserFactory.create(
            partner=partner_with_program_access
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_with_program_access,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            name="Role with approval permission",
        )
        cls.user_with_approval_permission_partner_without_program_access = UserFactory.create(
            partner=partner_without_program_access
        )
        cls.create_user_role_with_permissions(
            cls.user_with_approval_permission_partner_without_program_access,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            cls.business_area,
            name="Role with approval permission",
        )
        cls.user_with_authorize_permission = UserFactory.create(partner=partner_with_program_access)
        cls.create_user_role_with_permissions(
            cls.user_with_authorize_permission,
            [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE],
            cls.business_area,
            name="Role with authorize permission",
        )
        cls.user_with_review_permission = UserFactory.create(partner=partner_with_program_access)
        cls.create_user_role_with_permissions(
            cls.user_with_review_permission,
            [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW],
            cls.business_area,
            name="Role with review permission",
        )
        cls.user_with_download_xlsx_permission = UserFactory.create(partner=partner_with_program_access)
        cls.create_user_role_with_permissions(
            cls.user_with_download_xlsx_permission,
            [Permissions.PM_DOWNLOAD_XLSX_FOR_FSP],
            cls.business_area,
            name="Role with download xlsx permission",
        )

        cls.user_with_BA_and_unicef_partner = UserFactory.create(
            partner=partner_unicef
        )  # depends on DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER
        cls.create_user_role_with_permissions(
            cls.user_with_BA_and_unicef_partner,
            [Permissions.PM_VIEW_LIST],
            cls.business_area,
            name="Role with view list permission",
        )
        cls.user_without_BA_and_unicef_partner = UserFactory.create(partner=partner_unicef)
        role = Role.objects.create(
            name="Partner role",
            permissions=[
                Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name,
                Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name,
                Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name,
                Permissions.PM_DOWNLOAD_XLSX_FOR_FSP.name,
            ],
        )
        partner_with_action_permissions_and_program_access = PartnerFactory.create(
            name="Partner with action permissions and program access"
        )
        partner_with_action_permissions_and_program_access.permissions = {
            str(cls.business_area.id): {
                "programs": {str(cls.program.id): []},
                "roles": [str(role.pk)],
            }
        }
        partner_with_action_permissions_and_program_access.save()
        partner_with_action_permissions_without_program_access = PartnerFactory.create(
            name="Partner with action permissions and without program access"
        )
        partner_with_action_permissions_without_program_access.permissions = {
            str(cls.business_area.id): {
                "programs": {str(cls.program2.id): []},
                "roles": [str(role.pk)],
            }
        }
        partner_with_action_permissions_without_program_access.save()
        cls.user_with_partner_action_permissions_and_program_access = UserFactory.create(
            partner=partner_with_action_permissions_and_program_access
        )
        cls.user_with_partner_action_permissions_without_program_access = UserFactory.create(
            partner=partner_with_action_permissions_without_program_access
        )

    def test_prepare_user_recipients_for_send_for_approval(self) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.SEND_FOR_APPROVAL.name)
        self.assertEqual(
            payment_notification.user_recipients.count(),
            3,
        )
        for recipient in [
            self.user_with_approval_permission_partner_unicef,
            self.user_with_approval_permission_partner_with_program_access,
            self.user_with_partner_action_permissions_and_program_access,
        ]:
            self.assertIn(
                recipient,
                payment_notification.user_recipients.all(),
            )
        self.assertNotIn(
            self.user_action_user,
            payment_notification.user_recipients.all(),
        )

    def test_prepare_user_recipients_for_approve(self) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.APPROVE.name)
        self.assertEqual(
            payment_notification.user_recipients.count(),
            2,
        )
        for recipient in [
            self.user_with_authorize_permission,
            self.user_with_partner_action_permissions_and_program_access,
        ]:
            self.assertIn(
                recipient,
                payment_notification.user_recipients.all(),
            )
        self.assertNotIn(
            self.user_action_user,
            payment_notification.user_recipients.all(),
        )

    def test_prepare_user_recipients_for_authorize(self) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.AUTHORIZE.name)
        self.assertEqual(
            payment_notification.user_recipients.count(),
            2,
        )
        for recipient in [
            self.user_with_review_permission,
            self.user_with_partner_action_permissions_and_program_access,
        ]:
            self.assertIn(
                recipient,
                payment_notification.user_recipients.all(),
            )
        self.assertNotIn(
            self.user_action_user,
            payment_notification.user_recipients.all(),
        )

    def test_prepare_user_recipients_for_release(self) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.REVIEW.name)
        self.assertEqual(
            payment_notification.user_recipients.count(),
            2,
        )
        for recipient in [
            self.user_with_download_xlsx_permission,
            self.user_with_partner_action_permissions_and_program_access,
        ]:
            self.assertIn(
                recipient,
                payment_notification.user_recipients.all(),
            )
        self.assertNotIn(
            self.user_action_user,
            payment_notification.user_recipients.all(),
        )

    def test_prepare_action_user_and_date_for_send_for_approval(self) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.SEND_FOR_APPROVAL.name)
        self.assertEqual(
            payment_notification.action_user,
            self.approval_process.sent_for_approval_by,
        )
        self.assertEqual(
            payment_notification.action_date,
            self.approval_process.sent_for_approval_date,
        )

    def test_prepare_action_user_and_date_for_approve(self) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.APPROVE.name)
        self.assertEqual(
            payment_notification.action_user,
            self.approval_approval.created_by,
        )
        self.assertEqual(
            payment_notification.action_date,
            self.approval_approval.created_at,
        )

    def test_prepare_action_user_and_date_for_authorize(self) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.AUTHORIZE.name)
        self.assertEqual(
            payment_notification.action_user,
            self.approval_authorization.created_by,
        )
        self.assertEqual(
            payment_notification.action_date,
            self.approval_authorization.created_at,
        )

    def test_prepare_action_user_and_date_for_release(self) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.REVIEW.name)
        self.assertEqual(
            payment_notification.action_user,
            self.approval_release.created_by,
        )
        self.assertEqual(
            payment_notification.action_date,
            self.approval_release.created_at,
        )

    @mock.patch("hct_mis_api.apps.payment.notifications.EmailMultiAlternatives.send")
    @override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
    def test_send_email_notification(self, mock_send: Any) -> None:
        payment_notification = PaymentNotification(self.payment_plan, PaymentPlan.Action.SEND_FOR_APPROVAL.name)
        payment_notification.send_email_notification()
        self.assertEqual(
            mock_send.call_count,
            3,
        )
