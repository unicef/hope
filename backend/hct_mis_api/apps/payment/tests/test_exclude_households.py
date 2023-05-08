from typing import Any
from unittest import mock

from freezegun import freeze_time

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan

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
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP], cls.business_area
        )

        cls.source_payment_plan = PaymentPlanFactory(is_follow_up=False, status=PaymentPlan.Status.FINISHED)

        cls.payment_plan = PaymentPlanFactory(
            source_payment_plan=cls.source_payment_plan, is_follow_up=True, status=PaymentPlan.Status.LOCKED
        )
        cls.another_payment_plan = PaymentPlanFactory()
        cls.payment_plan_id = encode_id_base64(cls.payment_plan.id, "PaymentPlan")

        hoh1 = IndividualFactory(household=None)
        cls.household_1 = HouseholdFactory(id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f51", head_of_household=hoh1)
        cls.payment_1 = PaymentFactory(parent=cls.payment_plan, household=cls.household_1, excluded=False)

        hoh2 = IndividualFactory(household=None)
        cls.household_2 = HouseholdFactory(id="4ccd6a58-d56a-4ad2-9448-dabca4cfcb84", head_of_household=hoh2)
        cls.payment_2 = PaymentFactory(parent=cls.payment_plan, household=cls.household_2, excluded=False)

        hoh3 = IndividualFactory(household=None)
        cls.household_3 = HouseholdFactory(id="e1bdabf2-a54a-40c4-b92d-166b79d10542", head_of_household=hoh3)
        cls.payment_3 = PaymentFactory(parent=cls.payment_plan, household=cls.household_3, excluded=False)

        hoh4 = IndividualFactory(household=None)
        cls.household_4 = HouseholdFactory(id="7e14efa4-3ff3-4947-aecc-b517c659ebda", head_of_household=hoh4)
        cls.payment_4 = PaymentFactory(parent=cls.another_payment_plan, household=cls.household_4, excluded=False)

    @freeze_time("2020-10-10")
    def test_exclude_households(self) -> None:
        household_unicef_id_1 = Household.objects.get(id=self.household_1.id).unicef_id
        household_unicef_id_2 = Household.objects.get(id=self.household_2.id).unicef_id

        self.graphql_request(
            request_string=EXCLUDE_HOUSEHOLD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.payment_plan_id,
                "excludedHouseholdsIds": [household_unicef_id_1, household_unicef_id_2],
            },
        )

        self.payment_plan.refresh_from_db()
        self.payment_1.refresh_from_db()
        self.payment_2.refresh_from_db()
        self.payment_3.refresh_from_db()

        self.assertEqual(self.payment_1.excluded, True)
        self.assertEqual(self.payment_2.excluded, True)
        self.assertEqual(self.payment_3.excluded, False)
        self.assertEqual(
            set(self.payment_plan.excluded_households_ids),
            {self.payment_1.household.unicef_id, self.payment_2.household.unicef_id},
        )

    def test_exclude_payment_raises_error_when_payment_plan_contains_already_excluded_payments(self) -> None:
        self.payment_1.excluded = True
        self.payment_2.excluded = True
        self.payment_1.save()
        self.payment_2.save()

        household_unicef_id_1 = Household.objects.get(id=self.household_1.id).unicef_id
        household_unicef_id_2 = Household.objects.get(id=self.household_2.id).unicef_id

        exclude_mutation_response = self.graphql_request(
            request_string=EXCLUDE_HOUSEHOLD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.payment_plan_id,
                "excludedHouseholdsIds": [household_unicef_id_1, household_unicef_id_2],
            },
        )

        assert "errors" in exclude_mutation_response
        self.assertEqual(
            exclude_mutation_response["errors"][0]["message"],
            "This Payment Plan already contains excluded households",
        )

    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_exclude_payment_raises_error_when_payment_not_belongs_to_payment_plan(
        self, get_exchange_rate_mock: Any
    ) -> None:
        household_unicef_id_1 = Household.objects.get(id=self.household_1.id).unicef_id
        household_unicef_id_4 = Household.objects.get(id=self.household_4.id).unicef_id

        exclude_mutation_response = self.graphql_request(
            request_string=EXCLUDE_HOUSEHOLD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.payment_plan_id,
                "excludedHouseholdsIds": [household_unicef_id_1, household_unicef_id_4],
            },
        )

        assert "errors" in exclude_mutation_response
        self.assertEqual(
            exclude_mutation_response["errors"][0]["message"],
            "These Households are not included in this Payment Plan",
        )
