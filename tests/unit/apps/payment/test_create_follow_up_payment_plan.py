import datetime

from tests.extras.test_utils.factories.account import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment, PaymentPlan

CREATE_FOLLOW_UP_MUTATION = """
mutation createFollowUpPaymentPlan($paymentPlanId: ID!, $dispersionStartDate: Date!, $dispersionEndDate: Date!) {
  createFollowUpPaymentPlan(
    paymentPlanId: $paymentPlanId, dispersionStartDate: $dispersionStartDate, dispersionEndDate: $dispersionEndDate
  ) {
    paymentPlan {
      status
      isFollowUp
      canCreateFollowUp
      totalWithdrawnHouseholdsCount
    }
  }
}
"""


class TestCreateFollowUpPaymentPlan(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(cls.user, [Permissions.PM_CREATE], cls.business_area)
        cls.payment_plan = PaymentPlanFactory(
            business_area=cls.business_area, status=PaymentPlan.Status.ACCEPTED, created_by=cls.user
        )
        PaymentFactory.create_batch(
            5, parent=cls.payment_plan, excluded=False, currency="PLN", status=Payment.STATUS_ERROR
        )

    def test_create_follow_up_pp_mutation(self) -> None:
        self.snapshot_graphql_request(
            request_string=CREATE_FOLLOW_UP_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                "dispersionStartDate": datetime.date(2022, 8, 25),
                "dispersionEndDate": datetime.date(2022, 8, 30),
            },
        )
