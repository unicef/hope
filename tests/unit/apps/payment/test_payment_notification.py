from typing import Any
from unittest import mock

from django.test import override_settings
from django.utils import timezone

from constance.test import override_config

from hct_mis_api.apps.account.models import Role
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import Approval, PaymentPlan
from hct_mis_api.apps.payment.notifications import PaymentNotification
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    PaymentPlanFactory,
)
from tests.extras.test_utils.factories.program import ProgramFactory


class TestPaymentNotification(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user_payment_plan_creator = UserFactory.create()
        cls.user_action_user = UserFactory.create()
        cls.program = ProgramFactory.create(business_area=cls.business_area)
        cls.program2 = ProgramFactory.create(business_area=cls.business_area)
        cls.payment_plan = PaymentPlanFactory.create(
            business_area=cls.business_area,
            created_by=cls.user_payment_plan_creator,
            program_cycle=cls.program.cycles.first(),
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
        cls.update_partner_access_to_program(partner_with_program_access, cls.program)

        partner_without_program_access = PartnerFactory.create(name="Partner without program access")
        cls.update_partner_access_to_program(partner_without_program_access, cls.program2)
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
        cls.update_partner_access_to_program(
            partner_with_action_permissions_and_program_access,
            cls.program,
        )
        cls.add_partner_role_in_business_area(
            partner_with_action_permissions_and_program_access,
            cls.business_area,
            [role],
        )
        partner_with_action_permissions_without_program_access = PartnerFactory.create(
            name="Partner with action permissions and without program access"
        )
        cls.update_partner_access_to_program(
            partner_with_action_permissions_without_program_access,
            cls.program2,
        )
        cls.add_partner_role_in_business_area(
            partner_with_action_permissions_without_program_access,
            cls.business_area,
            [role],
        )

        cls.user_with_partner_action_permissions_and_program_access = UserFactory.create(
            partner=partner_with_action_permissions_and_program_access
        )
        cls.user_with_partner_action_permissions_without_program_access = UserFactory.create(
            partner=partner_with_action_permissions_without_program_access
        )

    def test_prepare_user_recipients_for_send_for_approval(self) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
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
        payment_notification = PaymentNotification(
            self.payment_plan, PaymentPlan.Action.APPROVE.name, self.user_action_user, f"{timezone.now():%-d %B %Y}"
        )
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
        payment_notification = PaymentNotification(
            self.payment_plan, PaymentPlan.Action.AUTHORIZE.name, self.user_action_user, f"{timezone.now():%-d %B %Y}"
        )
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
        payment_notification = PaymentNotification(
            self.payment_plan, PaymentPlan.Action.REVIEW.name, self.user_action_user, f"{timezone.now():%-d %B %Y}"
        )
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

    @mock.patch("hct_mis_api.apps.payment.notifications.MailjetClient.send_email")
    @override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
    def test_send_email_notification(self, mock_send: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        payment_notification.send_email_notification()
        self.assertEqual(
            mock_send.call_count,
            1,
        )

    @mock.patch("hct_mis_api.apps.payment.notifications.MailjetClient.send_email")
    @override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    def test_send_email_notification_subject_test_env(self, mock_send: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        self.assertEqual(payment_notification.email.subject, "[test] Payment pending for Approval")

    @mock.patch("hct_mis_api.apps.payment.notifications.MailjetClient.send_email")
    @override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
    @override_settings(EMAIL_SUBJECT_PREFIX="")
    def test_send_email_notification_subject_prod_env(self, mock_send: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        self.assertEqual(payment_notification.email.subject, "Payment pending for Approval")

    @mock.patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @override_config(
        SEND_PAYMENT_PLANS_NOTIFICATION=True, ENABLE_MAILJET=True, MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1
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
        self.assertEqual(len(payment_notification.email.recipients), 2)
        self.assertIn(
            "catchallemail@email.com",
            payment_notification.email.recipients,
        )
        self.assertIn(
            "catchallemail2@email.com",
            payment_notification.email.recipients,
        )
        self.assertEqual(
            mock_post.call_count,
            1,
        )

    @mock.patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @override_config(
        SEND_PAYMENT_PLANS_NOTIFICATION=True, ENABLE_MAILJET=True, MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1
    )
    def test_send_email_notification_without_catch_all_email(self, mock_post: Any) -> None:
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        payment_notification.send_email_notification()
        self.assertEqual(len(payment_notification.email.recipients), 3)
        self.assertIn(
            self.user_with_approval_permission_partner_unicef.email,
            payment_notification.email.recipients,
        )
        self.assertIn(
            self.user_with_approval_permission_partner_with_program_access.email,
            payment_notification.email.recipients,
        )
        self.assertIn(
            self.user_with_partner_action_permissions_and_program_access.email,
            payment_notification.email.recipients,
        )
        self.assertEqual(
            mock_post.call_count,
            1,
        )

    @mock.patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @override_config(
        SEND_PAYMENT_PLANS_NOTIFICATION=True, ENABLE_MAILJET=True, MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1
    )
    @override_settings(ENV="prod")
    def test_send_email_notification_exclude_superuser(self, mock_post: Any) -> None:
        self.user_with_approval_permission_partner_unicef.is_superuser = True
        self.user_with_approval_permission_partner_unicef.save()
        payment_notification = PaymentNotification(
            self.payment_plan,
            PaymentPlan.Action.SEND_FOR_APPROVAL.name,
            self.user_action_user,
            f"{timezone.now():%-d %B %Y}",
        )
        payment_notification.send_email_notification()
        self.assertEqual(len(payment_notification.email.recipients), 2)
        self.assertIn(
            self.user_with_approval_permission_partner_with_program_access.email,
            payment_notification.email.recipients,
        )
        self.assertIn(
            self.user_with_partner_action_permissions_and_program_access.email,
            payment_notification.email.recipients,
        )
        self.assertEqual(
            mock_post.call_count,
            1,
        )
