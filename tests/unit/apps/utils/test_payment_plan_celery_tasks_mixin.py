from django.test import TestCase
from django.urls import reverse

from parameterized import parameterized
from rest_framework import status

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan


class TestPaymentPlanCeleryTasksMixin(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()

        cls.user = UserFactory()
        cls.user.username = "admin"
        cls.password = User.objects.make_random_password()
        cls.user.set_password(cls.password)
        cls.user.is_staff = True
        cls.user.is_superuser = True
        cls.user.is_active = True
        cls.user.save()

        cls.payment_plan = PaymentPlanFactory()

    def setUp(self) -> None:
        self.url = reverse("admin:payment_paymentplan_change", args=[self.payment_plan.id])

    @parameterized.expand(
        [
            (PaymentPlan.Status.PREPARING, None, 'id="btn-restart_preparing_payment_plan"'),
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
