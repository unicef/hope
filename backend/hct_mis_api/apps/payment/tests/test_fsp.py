import json

from hct_mis_api.apps.payment.fixtures import FinancialServiceProviderFactory
from hct_mis_api.apps.payment.models import GenericPayment
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.account.permissions import Permissions


class TestFSPSetup(APITestCase):
    CHOOSE_DELIVERY_MECHANISMS_MUTATION = """
mutation ChooseDeliveryMechanismsForPaymentPlan($input: ChooseDeliveryMechanismsForPaymentPlanInput!) {
  chooseDeliveryMechanismsForPaymentPlan(input: $input) {
    paymentPlan {
      id
      deliveryMechanisms
    }
  }
}
"""

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PAYMENT_MODULE_CREATE], BusinessArea.objects.get(slug="afghanistan")
        )

    def test_choosing_delivery_mechanism_order(self):
        payment_plan = PaymentPlanFactory(total_households_count=1)
        # FinancialServiceProviderFactory.create()

        encoded_payment_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        create_program_mutation_variables_without_delivery_mechanisms = dict(
            input=dict(
                paymentPlanId=encoded_payment_id,
                deliveryMechanisms=[],
            )
        )
        response_without_mechanisms = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables_without_delivery_mechanisms,
        )
        payment_plan_without_delivery_mechanisms = response_without_mechanisms["data"][
            "chooseDeliveryMechanismsForPaymentPlan"
        ]["paymentPlan"]
        self.assertEqual(payment_plan_without_delivery_mechanisms["id"], encoded_payment_id)
        self.assertEqual(payment_plan_without_delivery_mechanisms["deliveryMechanisms"], [])

        create_program_mutation_variables_with_delivery_mechanisms = dict(
            input=dict(
                paymentPlanId=encoded_payment_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER],
            )
        )
        response_with_mechanisms = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables_with_delivery_mechanisms,
        )
        payment_plan_with_delivery_mechanisms = response_with_mechanisms["data"][
            "chooseDeliveryMechanismsForPaymentPlan"
        ]["paymentPlan"]
        self.assertEqual(payment_plan_with_delivery_mechanisms["id"], encoded_payment_id)
        self.assertEqual(
            json.loads(payment_plan_with_delivery_mechanisms["deliveryMechanisms"][0]),
            {"name": GenericPayment.DELIVERY_TYPE_TRANSFER, "order": 1},
        )
        self.assertEqual(
            json.loads(payment_plan_with_delivery_mechanisms["deliveryMechanisms"][1]),
            {"name": GenericPayment.DELIVERY_TYPE_VOUCHER, "order": 2},
        )
