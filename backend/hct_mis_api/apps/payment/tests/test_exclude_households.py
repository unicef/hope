from freezegun import freeze_time

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory

EXCLUDE_HOUSEHOLD_MUTATION = """
mutation excludeHouseholds($paymentPlanId: ID!, $excludedHouseholdsIds: [String]!) {
  excludeHouseholds(
    paymentPlanId: $paymentPlanId,
    excludedHouseholdsIds: $excludedHouseholdsIds
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

    @freeze_time("2020-10-10")
    def test_exclude_households(self) -> None:
        payment_plan = PaymentPlanFactory()

        hoh1 = IndividualFactory(household=None)
        household_1 = HouseholdFactory(id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f51", head_of_household=hoh1)
        payment_1 = PaymentFactory(parent=payment_plan, household=household_1, excluded=False)

        hoh2 = IndividualFactory(household=None)
        household_2 = HouseholdFactory(id="4ccd6a58-d56a-4ad2-9448-dabca4cfcb84", head_of_household=hoh2)
        payment_2 = PaymentFactory(parent=payment_plan, household=household_2, excluded=False)

        hoh3 = IndividualFactory(household=None)
        household_3 = HouseholdFactory(id="e1bdabf2-a54a-40c4-b92d-166b79d10542", head_of_household=hoh3)
        payment_3 = PaymentFactory(parent=payment_plan, household=household_3, excluded=False)

        household_unicef_id_1 = Household.objects.get(id=household_1.id).unicef_id
        household_unicef_id_2 = Household.objects.get(id=household_2.id).unicef_id

        self.graphql_request(
            request_string=EXCLUDE_HOUSEHOLD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": encode_id_base64(payment_plan.id, "PaymentPlan"),
                "excludedHouseholdsIds": [household_unicef_id_1, household_unicef_id_2],
            },
        )

        payment_plan.refresh_from_db()
        payment_1.refresh_from_db()
        payment_2.refresh_from_db()
        payment_3.refresh_from_db()

        self.assertEqual(payment_1.excluded, True)
        self.assertEqual(payment_2.excluded, True)
        self.assertEqual(payment_3.excluded, False)
        self.assertEqual(
            set(payment_plan.excluded_households_ids), {payment_1.household.unicef_id, payment_2.household.unicef_id}
        )
