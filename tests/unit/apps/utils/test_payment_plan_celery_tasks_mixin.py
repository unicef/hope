from django.contrib import messages
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from parameterized import parameterized
from rest_framework import status

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.utils import generate_cache_key


class TestPaymentPlanCeleryTasksMixin(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(name="Test ABC")

        cls.user = UserFactory()
        cls.user.username = "admin"
        cls.password = User.objects.make_random_password()
        cls.user.set_password(cls.password)
        cls.user.is_staff = True
        cls.user.is_superuser = True
        cls.user.is_active = True
        cls.user.save()

        cls.payment_plan = PaymentPlanFactory(
            program_cycle=cls.program.cycles.first(),
            created_by=cls.user,
        )

    def setUp(self) -> None:
        self.url = reverse("admin:payment_paymentplan_change", args=[self.payment_plan.id])

    @parameterized.expand(
        [
            (
                PaymentPlan.Status.LOCKED,
                PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
                'id="btn-restart_importing_entitlements_xlsx_file"',
            ),
            (
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
                'id="btn-restart_importing_reconciliation_xlsx_file"',
            ),
            (
                PaymentPlan.Status.LOCKED,
                PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
                'id="btn-restart_exporting_template_for_entitlement"',
            ),
            (
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
                'id="btn-restart_exporting_payment_plan_list"',
            ),
        ]
    )
    def test_buttons_are_visible_according_to_status(
        self, pp_status: str, background_action_status: str, html_element: str
    ) -> None:
        self.client.login(username=self.user.username, password=self.password)

        self.payment_plan.status = pp_status
        self.payment_plan.background_action_status = background_action_status
        self.payment_plan.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(html_element, response.rendered_content)

    @override_settings(ROOT_TOKEN="test-token123")
    def test_restart_prepare_payment_plan_task_success(self) -> None:
        self.client.login(username=self.user.username, password=self.password)
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        payment_plan.refresh_from_db()
        response = self.client.post(
            reverse("admin:payment_paymentplan_restart_preparing_payment_plan", args=[payment_plan.id]),
            HTTP_X_ROOT_TOKEN="test-token123",
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.assertEqual(
            list(messages.get_messages(response.wsgi_request))[0].message,
            f"Task restarted for Payment Plan: {payment_plan.unicef_id}",
        )

    @override_settings(ROOT_TOKEN="test-token123")
    def test_restart_prepare_payment_plan_task_incorrect_status(self) -> None:
        self.client.login(username=self.user.username, password=self.password)
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.LOCKED,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        payment_plan.refresh_from_db()
        response = self.client.post(
            reverse("admin:payment_paymentplan_restart_preparing_payment_plan", args=[payment_plan.id]),
            HTTP_X_ROOT_TOKEN="test-token123",
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.assertEqual(
            list(messages.get_messages(response.wsgi_request))[0].message,
            f"The Payment Plan must has the status {PaymentPlan.Status.OPEN}",
        )

    @override_settings(ROOT_TOKEN="test-token123")
    def test_restart_prepare_payment_plan_task_already_running(self) -> None:
        self.client.login(username=self.user.username, password=self.password)
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        payment_plan.refresh_from_db()
        # set the cache to simulate an already running task
        cache_key = generate_cache_key(
            {
                "task_name": "prepare_payment_plan_task",
                "payment_plan_id": str(payment_plan.id),
            }
        )
        cache.set(cache_key, True, timeout=600)

        response = self.client.post(
            reverse("admin:payment_paymentplan_restart_preparing_payment_plan", args=[payment_plan.id]),
            HTTP_X_ROOT_TOKEN="test-token123",
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.assertEqual(
            list(messages.get_messages(response.wsgi_request))[0].message,
            f"Task is already running for Payment Plan {payment_plan.unicef_id}.",
        )
