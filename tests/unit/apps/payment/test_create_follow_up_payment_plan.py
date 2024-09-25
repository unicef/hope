from django.utils import timezone

from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment, PaymentPlan

CREATE_FOLLOW_UP_MUTATION = """
mutation createFollowUpPaymentPlan($paymentPlanId: ID!, $dispersionStartDate: Date!, $dispersionEndDate: Date!) {
  createFollowUpPaymentPlan(
    paymentPlanId: $paymentPlanId, dispersionStartDate: $dispersionStartDate, dispersionEndDate: $dispersionEndDate
  ) {
    paymentPlan {
      status
      isFollowUp
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
        cls.create_user_role_with_permissions(cls.user, [Permissions.PM_CREATE], cls.business_area)
        cls.payment_plan = PaymentPlanFactory(business_area=cls.business_area, status=PaymentPlan.Status.ACCEPTED)
        PaymentFactory.create_batch(
            5, parent=cls.payment_plan, excluded=False, currency="PLN", status=Payment.STATUS_ERROR
        )

    def test_export_pdf_payment_plan_summary_mutation(self) -> None:
        self.snapshot_graphql_request(
            request_string=CREATE_FOLLOW_UP_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                "dispersionStartDate": timezone.datetime(2022, 8, 25, tzinfo=utc),
                "dispersionEndDate": timezone.datetime(2022, 8, 30, tzinfo=utc),
            },
        )
