from typing import Any
from unittest import mock
from unittest.mock import patch

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    PaymentPlan,
)
from tests.extras.test_utils.factories.account import UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanSplitFactory,
    generate_delivery_mechanisms,
)

SPLIT_PAYMENT_MUTATION = """
mutation splitPaymentPlan($paymentPlanId: ID!, $paymentsNo: Int, $splitType: String!) {
  splitPaymentPlan(
    paymentPlanId: $paymentPlanId,
    paymentsNo: $paymentsNo,
    splitType: $splitType
){
    paymentPlan {
        status
    }
  }
}
"""


class TestSplitPaymentPlan(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(cls.user, [Permissions.PM_SPLIT], cls.business_area)
        generate_delivery_mechanisms()

    @patch("hct_mis_api.apps.payment.models.PaymentPlanSplit.MAX_CHUNKS")
    def test_split_payment_plan_mutation(self, max_chunks_mock: Any) -> None:
        max_chunks_mock.__get__ = mock.Mock(return_value=10)
        dm_cash = DeliveryMechanism.objects.get(code="cash")
        fsp_1 = FinancialServiceProviderFactory(
            name="Test FSP 1",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            vision_vendor_number=333222111,
            payment_gateway_id="test_payment_gateway_id",
        )
        fsp_1.delivery_mechanisms.add(dm_cash)
        pp = PaymentPlanFactory(
            business_area=self.business_area,
            status=PaymentPlan.Status.ACCEPTED,
            created_by=self.user,
            financial_service_provider=fsp_1,
            delivery_mechanism=dm_cash,
        )
        split = PaymentPlanSplitFactory(payment_plan=pp, sent_to_payment_gateway=True)
        #  'Payment plan is already sent to payment gateway'
        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 2,
                "splitType": "BY_RECORDS",
            },
        )

        # 'Payment plan must be accepted to make a split'
        split.sent_to_payment_gateway = False
        split.save()
        pp.status = PaymentPlan.Status.OPEN
        pp.save()
        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 2,
                "splitType": "BY_RECORDS",
            },
        )

        # 'Payment Number is required for split by records'
        pp.status = PaymentPlan.Status.ACCEPTED
        pp.save()
        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 0,
                "splitType": "BY_RECORDS",
            },
        )

        # 'No payments to split'
        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 2,
                "splitType": "BY_RECORDS",
            },
        )

        # 'Cannot split Payment Plan into more than 2 parts'
        PaymentFactory.create_batch(10, parent=pp, excluded=False, currency="PLN")
        max_chunks_mock.__get__ = mock.Mock(return_value=2)
        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 2,
                "splitType": "BY_RECORDS",
            },
        )

        # successful
        max_chunks_mock.__get__ = mock.Mock(return_value=10)
        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 10,
                "splitType": "BY_RECORDS",
            },
        )

        # successful
        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 10,
                "splitType": "BY_COLLECTOR",
            },
        )
