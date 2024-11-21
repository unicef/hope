from unittest.mock import Mock, patch

from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from django.test import RequestFactory, TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.admin import PaymentPlanAdmin
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.utils import generate_cache_key
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestAdminPaymentPlan(TestCase):
    def setUp(self) -> None:
        create_afghanistan()
        user = UserFactory()

        self.factory = RequestFactory()
        self.site = AdminSite()
        self.request = self.factory.post("/admin123/")
        self.admin = PaymentPlanAdmin(PaymentPlan, self.site)
        self.request.user = user
        # message middleware
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()
        setattr(self.request, "_messages", FallbackStorage(self.request))  # noqa: B010

        self.program = ProgramFactory(name="Test AAA")

    @patch(
        "hct_mis_api.apps.payment.admin.PaymentPlanAdmin.has_restart_prepare_payment_plan_task_permission",
        return_value=True,
    )
    def test_restart_prepare_payment_plan_task_success(self, mock_permission: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.PREPARING,
            program=self.program,
        )
        queryset = PaymentPlan.objects.filter(id=payment_plan.id)
        payment_plan.refresh_from_db()
        self.admin.restart_prepare_payment_plan_task(self.request, queryset)

        messages = list(get_messages(self.request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Task restarted for Payment Plan(s): {payment_plan.unicef_id}")
        self.assertEqual(messages[0].level_tag, "success")

    @patch(
        "hct_mis_api.apps.payment.admin.PaymentPlanAdmin.has_restart_prepare_payment_plan_task_permission",
        return_value=True,
    )
    def test_restart_prepare_payment_plan_task_incorrect_status(self, mock_permission: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.IN_APPROVAL,
            program=self.program,
        )
        queryset = PaymentPlan.objects.filter(id=payment_plan.id)
        payment_plan.refresh_from_db()
        self.admin.restart_prepare_payment_plan_task(self.request, queryset)

        # Assert warning message
        messages = list(get_messages(self.request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "The Payment Plan(s) must have the status PREPARING",
        )
        self.assertEqual(messages[0].level_tag, "warning")

    @patch(
        "hct_mis_api.apps.payment.admin.PaymentPlanAdmin.has_restart_prepare_payment_plan_task_permission",
        return_value=True,
    )
    def test_restart_prepare_payment_plan_task_already_running(self, mock_permission: Mock) -> None:
        payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.PREPARING, program=self.program)
        payment_plan.refresh_from_db()
        # set the cache to simulate an already running task
        cache_key = generate_cache_key(
            {
                "task_name": "prepare_payment_plan_task",
                "payment_plan_id": str(payment_plan.id),
            }
        )
        cache.set(cache_key, True, timeout=60)

        queryset = PaymentPlan.objects.filter(id=payment_plan.id)
        self.admin.restart_prepare_payment_plan_task(self.request, queryset)

        messages = list(get_messages(self.request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"Task is already running for Payment Plan {payment_plan.unicef_id}.",
        )
        self.assertEqual(messages[0].level_tag, "error")

    @patch(
        "hct_mis_api.apps.payment.admin.PaymentPlanAdmin.has_restart_prepare_payment_plan_task_permission",
        return_value=True,
    )
    def test_restart_prepare_payment_plan_task_mixed_statuses(self, mock_permission: Mock) -> None:
        payment_plan_1 = PaymentPlanFactory(status=PaymentPlan.Status.PREPARING, program=self.program)
        payment_plan_2 = PaymentPlanFactory(status=PaymentPlan.Status.FINISHED, program=self.program)
        payment_plan_3 = PaymentPlanFactory(status=PaymentPlan.Status.PREPARING, program=self.program)
        payment_plan_1.refresh_from_db()
        payment_plan_2.refresh_from_db()
        payment_plan_3.refresh_from_db()

        # set the cache for payment_plan_3
        cache_key = generate_cache_key(
            {
                "task_name": "prepare_payment_plan_task",
                "payment_plan_id": str(payment_plan_3.id),
            }
        )
        cache.set(cache_key, True, timeout=60)

        queryset = PaymentPlan.objects.filter(id__in=[payment_plan_1.id, payment_plan_2.id, payment_plan_3.id])
        self.admin.restart_prepare_payment_plan_task(self.request, queryset)

        messages = list(get_messages(self.request))
        self.assertEqual(len(messages), 3)
        self.assertEqual(str(messages[0]), "The Payment Plan(s) must have the status PREPARING")
        self.assertEqual(messages[0].level_tag, "warning")
        self.assertEqual(str(messages[1]), f"Task is already running for Payment Plan {payment_plan_3.unicef_id}.")
        self.assertEqual(messages[1].level_tag, "error")
        self.assertEqual(str(messages[2]), f"Task restarted for Payment Plan(s): {payment_plan_1.unicef_id}")
        self.assertEqual(messages[2].level_tag, "success")
