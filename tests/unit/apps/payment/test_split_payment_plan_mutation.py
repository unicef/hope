from typing import Any
from unittest import mock
from unittest.mock import patch

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    PaymentPlan,
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
        pp = PaymentPlanFactory(business_area=self.business_area, status=PaymentPlan.Status.ACCEPTED)

        dm_cash = DeliveryMechanism.objects.get(code="cash")

        fsp_1 = FinancialServiceProviderFactory(
            name="Test FSP 1",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            vision_vendor_number=333222111,
            payment_gateway_id="test_payment_gateway_id",
        )
        fsp_1.delivery_mechanisms.add(dm_cash)
        fsp_2 = FinancialServiceProviderFactory(
            name="Test FSP 2",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
            vision_vendor_number=111222333,
        )
        fsp_2.delivery_mechanisms.add(dm_cash)
        delivery_mech_for_pp = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=pp,
            financial_service_provider=fsp_1,
            delivery_mechanism=dm_cash,
            delivery_mechanism_order=1,
            sent_to_payment_gateway=True,
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=pp,
            financial_service_provider=fsp_2,
            delivery_mechanism=dm_cash,
            delivery_mechanism_order=2,
        )
        # check delivery mechanisms count
        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 2,
                "splitType": "BY_RECORDS",
            },
        )
        # remove unused delivery mechanism
        DeliveryMechanismPerPaymentPlan.objects.filter(
            payment_plan=pp,
            financial_service_provider=fsp_2,
            delivery_mechanism_order=2,
        ).delete()

        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 2,
                "splitType": "BY_RECORDS",
            },
        )

        # check correct PaymentPlan status
        delivery_mech_for_pp.sent_to_payment_gateway = False
        delivery_mech_for_pp.save()
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

        # check PaymentPlanSplit.MAX_CHUNKS
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

        self.snapshot_graphql_request(
            request_string=SPLIT_PAYMENT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.id_to_base64(pp.id, "PaymentPlanNode"),
                "paymentsNo": 10,
                "splitType": "BY_COLLECTOR",
            },
        )
