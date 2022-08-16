from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
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

        encoded_payment_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        create_program_mutation_variables = dict(
            input=dict(
                paymentPlanId=encoded_payment_id,
                deliveryMechanisms=[],
            )
        )

        response = self.graphql_request(
            request_string=self.CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=create_program_mutation_variables,
        )
        payment_plan = response["data"]["chooseDeliveryMechanismsForPaymentPlan"]["paymentPlan"]
        self.assertEqual(payment_plan["id"], encoded_payment_id)
        self.assertEqual(payment_plan["deliveryMechanisms"], [])
