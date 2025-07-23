from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentPlanFactory

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import PaymentPlan

EXPORT_PDF_MUTATION = """
mutation exportPdfPPSummary($paymentPlanId: ID!) {
  exportPdfPaymentPlanSummary(paymentPlanId: $paymentPlanId) {
    paymentPlan {
      status
    }
  }
}
"""


class TestExportPDFPaymentPlanSummary(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(cls.user, [Permissions.PM_EXPORT_PDF_SUMMARY], cls.business_area)
        cls.payment_plan = PaymentPlanFactory(
            business_area=cls.business_area,
            status=PaymentPlan.Status.ACCEPTED,
            created_by=cls.user,
        )

    def test_export_pdf_payment_plan_summary_mutation(self) -> None:
        self.snapshot_graphql_request(
            request_string=EXPORT_PDF_MUTATION,
            context={"user": self.user},
            variables={"paymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode")},
        )
