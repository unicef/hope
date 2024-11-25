from unittest.mock import Mock, patch

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.urls import reverse

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.admin import PaymentPlanAdmin
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestAdminPaymentPlan(TestCase):
    def setUp(self) -> None:
        create_afghanistan()
        user = UserFactory(is_superuser=True)
        self.program = ProgramFactory(name="Test ABC")
        self.payment_plan_1 = PaymentPlanFactory(
            status=PaymentPlan.Status.PREPARING,
            program=self.program,
        )

        self.factory = RequestFactory()

        self.request = self.factory.post(
            reverse("admin:payment_paymentplan_change", args=[str(self.payment_plan_1.pk)])
        )
        self.request.user = user
        self.request.headers = {"x-root-token": "test-token123"}  # type: ignore
        self.patcher = patch("django.conf.settings.ROOT_TOKEN", "test-token123")
        self.mock_root_token = self.patcher.start()

        self.admin = PaymentPlanAdmin(PaymentPlan, AdminSite())

    def tearDown(self) -> None:
        self.patcher.stop()
        super().tearDown()

    @patch.object(PaymentPlanAdmin, "get_object")
    def test_restart_prepare_payment_plan_task_success(self, mock_get_object: Mock) -> None:
        mock_get_object.return_value = self.payment_plan_1

        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.PREPARING,
            program=self.program,
        )
        payment_plan.refresh_from_db()

        mock_get_object.return_value = payment_plan

        # self.admin.restart_preparing_payment_plan(self.request, str(self.payment_plan_1.pk))

        # messages = list(get_messages(self.request))
        # self.assertEqual(len(messages), 1)
        # self.assertEqual(str(messages[0]), f"Task restarted for Payment Plan: {payment_plan.unicef_id}")
        # self.assertEqual(messages[0].level_tag, "success")

    # @patch(
    #     "hct_mis_api.apps.utils.security.is_root",
    #     return_value=True,
    # )
    # def test_restart_prepare_payment_plan_task_incorrect_status(self, mock_permission: Mock) -> None:
    #     payment_plan = PaymentPlanFactory(
    #         status=PaymentPlan.Status.IN_APPROVAL,
    #         program=self.program,
    #     )
    #     payment_plan.refresh_from_db()
    #     self.admin.restart_preparing_payment_plan(self.request, str(payment_plan.pk))
    #     # check message
    #     messages = list(get_messages(self.request))
    #     self.assertEqual(len(messages), 1)
    #     self.assertEqual(
    #         str(messages[0]),
    #         "The Payment Plan(s) must have the status PREPARING",
    #     )
    #     self.assertEqual(messages[0].level_tag, "warning")
    #
    # @patch(
    #     "hct_mis_api.apps.utils.security.is_root",
    #     return_value=True,
    # )
    # def test_restart_prepare_payment_plan_task_already_running(self, mock_permission: Mock) -> None:
    #     payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.PREPARING, program=self.program)
    #     payment_plan.refresh_from_db()
    #     # set the cache to simulate an already running task
    #     cache_key = generate_cache_key(
    #         {
    #             "task_name": "prepare_payment_plan_task",
    #             "payment_plan_id": str(payment_plan.id),
    #         }
    #     )
    #     cache.set(cache_key, True, timeout=60)
    #     self.admin.restart_preparing_payment_plan(self.request, str(payment_plan.pk))
    #
    #     messages = list(get_messages(self.request))
    #     self.assertEqual(len(messages), 1)
    #     self.assertEqual(
    #         str(messages[0]),
    #         f"Task is already running for Payment Plan {payment_plan.unicef_id}.",
    #     )
    #     self.assertEqual(messages[0].level_tag, "error")
