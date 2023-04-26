from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory

EXCLUDE_HOUSEHOLD_MUTATION = """
mutation excludeHouseholds($paymentPlanId: ID!, $householdIds: [ID]!) {
  excludeHouseholds(
        paymentPlanId: $paymentPlanId,
        householdIds: $householdIds
    ) {
    paymentPlan {
            id
        }
    }
}
"""


class TestExcludeHouseholds(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_exclude_households(self) -> None:
        payment_plan = PaymentPlanFactory()

        hoh1 = IndividualFactory(household=None)
        household_1 = HouseholdFactory(head_of_household=hoh1)
        payment_1 = PaymentFactory(parent=payment_plan, household=household_1, excluded=False)

        hoh2 = IndividualFactory(household=None)
        household_2 = HouseholdFactory(head_of_household=hoh2)
        payment_2 = PaymentFactory(parent=payment_plan, household=household_2, excluded=False)

        self.graphql_request(
            request_string=EXCLUDE_HOUSEHOLD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": encode_id_base64(payment_plan.id, "PaymentPlan"),
                "householdIds": [
                    encode_id_base64(household_1.id, "Household"),
                    encode_id_base64(household_2.id, "Household"),
                ],
            },
        )

        payment_plan.refresh_from_db()
        payment_1.refresh_from_db()
        payment_2.refresh_from_db()

        self.assertEqual(payment_1.excluded, True)
        self.assertEqual(payment_2.excluded, True)
        self.assertEqual(payment_plan.contains_excluded, True)
