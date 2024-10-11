from typing import Any
from unittest import mock

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.celery_tasks import payment_plan_exclude_beneficiaries
from hct_mis_api.apps.payment.fixtures import (
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
)
from hct_mis_api.apps.payment.models import PaymentPlan

EXCLUDE_HOUSEHOLD_MUTATION = """
mutation excludeHouseholds($paymentPlanId: ID!, $excludedHouseholdsIds: [String]!, $exclusionReason: String) {
  excludeHouseholds(
    paymentPlanId: $paymentPlanId,
    excludedHouseholdsIds: $excludedHouseholdsIds,
    exclusionReason: $exclusionReason
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
        cls.program = RealProgramFactory()
        cls.program_cycle = cls.program.cycles.first()

        cls.source_payment_plan = PaymentPlanFactory(
            is_follow_up=False, status=PaymentPlan.Status.FINISHED, program_cycle=cls.program_cycle
        )

        cls.payment_plan = PaymentPlanFactory(
            source_payment_plan=cls.source_payment_plan,
            is_follow_up=True,
            status=PaymentPlan.Status.LOCKED,
            program_cycle=cls.program_cycle,
        )
        cls.another_payment_plan = PaymentPlanFactory()
        cls.payment_plan_id = encode_id_base64(cls.payment_plan.id, "PaymentPlan")

        hoh1 = IndividualFactory(household=None)
        cls.household_1 = HouseholdFactory(id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f51", head_of_household=hoh1)
        cls.payment_1 = PaymentFactory(
            parent=cls.payment_plan, household=cls.household_1, excluded=False, currency="PLN"
        )

        hoh2 = IndividualFactory(household=None)
        cls.household_2 = HouseholdFactory(id="4ccd6a58-d56a-4ad2-9448-dabca4cfcb84", head_of_household=hoh2)
        cls.payment_2 = PaymentFactory(
            parent=cls.payment_plan, household=cls.household_2, excluded=False, currency="PLN"
        )

        hoh3 = IndividualFactory(household=None)
        cls.household_3 = HouseholdFactory(id="e1bdabf2-a54a-40c4-b92d-166b79d10542", head_of_household=hoh3)
        cls.payment_3 = PaymentFactory(
            parent=cls.payment_plan, household=cls.household_3, excluded=False, currency="PLN"
        )

        hoh4 = IndividualFactory(household=None)
        cls.household_4 = HouseholdFactory(id="7e14efa4-3ff3-4947-aecc-b517c659ebda", head_of_household=hoh4)
        cls.payment_4 = PaymentFactory(
            parent=cls.another_payment_plan, household=cls.household_4, excluded=False, currency="PLN"
        )

    def test_payment_plan_within_not_status_open_or_lock(self) -> None:
        payment_plan_id = encode_id_base64(self.source_payment_plan.id, "PaymentPlan")

        exclude_mutation_response = self.graphql_request(
            request_string=EXCLUDE_HOUSEHOLD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": payment_plan_id,
                "excludedHouseholdsIds": [Household.objects.get(id=self.household_1.id).unicef_id],
            },
        )

        assert "errors" in exclude_mutation_response
        self.assertEqual(
            exclude_mutation_response["errors"][0]["message"],
            "Beneficiary can be excluded only for 'Open' or 'Locked' status of Payment Plan",
        )

    def test_exclude_hh_without_permissions(self) -> None:
        payment_plan_id = encode_id_base64(self.source_payment_plan.id, "PaymentPlan")
        user_with_out_perms = UserFactory.create()

        exclude_mutation_response = self.graphql_request(
            request_string=EXCLUDE_HOUSEHOLD_MUTATION,
            context={"user": user_with_out_perms},
            variables={
                "paymentPlanId": payment_plan_id,
                "excludedHouseholdsIds": [Household.objects.first().unicef_id],
            },
        )

        assert "errors" in exclude_mutation_response
        self.assertEqual(
            exclude_mutation_response["errors"][0]["message"],
            "Permission Denied: User does not have correct permission.",
        )

    def test_exclude_households_mutation(self) -> None:
        household_unicef_id_1 = Household.objects.get(id=self.household_1.id).unicef_id

        self.graphql_request(
            request_string=EXCLUDE_HOUSEHOLD_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.payment_plan_id,
                "excludedHouseholdsIds": [household_unicef_id_1],
                "exclusionReason": "I do not like those households",
            },
        )

        self.payment_plan.refresh_from_db()

        self.assertEqual(
            self.payment_plan.background_action_status, PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
        )
        self.assertEqual(self.payment_plan.exclude_household_error, "")

    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_exclude_payment_with_wrong_hh_ids(self, get_exchange_rate_mock: Any) -> None:
        self.payment_1.excluded = True
        self.payment_2.excluded = True
        self.payment_1.save()
        self.payment_2.save()
        self.payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
        self.payment_plan.save(update_fields=["background_action_status"])

        hh_unicef_id_1 = Household.objects.get(id=self.household_1.id).unicef_id
        wrong_hh_id = "INVALID_ID"

        self.assertEqual(self.payment_plan.exclusion_reason, "")

        payment_plan_exclude_beneficiaries(
            payment_plan_id=self.payment_plan.pk,
            excluding_hh_ids=[hh_unicef_id_1, wrong_hh_id],
            exclusion_reason="reason exclusion Error 123",
        )
        self.payment_plan.refresh_from_db()
        error_msg = f"['Household {wrong_hh_id} is not part of this Follow-up Payment Plan.']"

        self.assertEqual(self.payment_plan.exclusion_reason, "reason exclusion Error 123")
        self.assertEqual(self.payment_plan.exclude_household_error, error_msg)
        self.assertIsNone(self.payment_plan.background_action_status)

    def test_exclude_all_households(self) -> None:
        self.payment_1.excluded = True
        self.payment_2.excluded = True
        self.payment_1.save()
        self.payment_2.save()
        self.payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
        self.payment_plan.save(update_fields=["background_action_status"])

        hh_unicef_id_1 = Household.objects.get(id=self.household_1.id).unicef_id
        hh_unicef_id_2 = Household.objects.get(id=self.household_2.id).unicef_id
        hh_unicef_id_3 = Household.objects.get(id=self.household_3.id).unicef_id

        self.assertEqual(self.payment_plan.exclusion_reason, "")

        payment_plan_exclude_beneficiaries(
            payment_plan_id=self.payment_plan.pk,
            excluding_hh_ids=[hh_unicef_id_1, hh_unicef_id_2, hh_unicef_id_3],
            exclusion_reason="reason exclude_all_households",
        )
        self.payment_plan.refresh_from_db()
        error_msg = "['Households cannot be entirely excluded from the Follow-up Payment Plan.']"

        self.assertEqual(self.payment_plan.exclusion_reason, "reason exclude_all_households")
        self.assertEqual(
            self.payment_plan.background_action_status, PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR
        )
        self.assertEqual(self.payment_plan.exclude_household_error, error_msg)

    def test_exclude_payment_error_when_payment_has_hard_conflicts(self) -> None:
        finished_payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.FINISHED,
            program=self.program,
            is_follow_up=False,
            program_cycle=self.program_cycle,
        )
        PaymentFactory(parent=finished_payment_plan, household=self.household_1, excluded=False, currency="PLN")

        self.payment_1.excluded = True
        self.payment_1.save()
        self.payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
        self.payment_plan.save(update_fields=["background_action_status"])
        self.household_1.refresh_from_db(fields=["unicef_id"])

        self.assertEqual(self.payment_plan.exclusion_reason, "")

        payment_plan_exclude_beneficiaries(
            payment_plan_id=self.payment_plan.pk, excluding_hh_ids=[], exclusion_reason="Undo HH_1"
        )

        self.assertEqual(set(self.payment_plan.excluded_households_ids), {self.payment_1.household.unicef_id})
        self.payment_plan.refresh_from_db()

        self.assertEqual(self.payment_plan.exclusion_reason, "Undo HH_1")
        self.assertEqual(
            self.payment_plan.background_action_status, PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR
        )

        error_msg = f"['It is not possible to undo exclude Household(s) with ID {self.household_1.unicef_id} because of hard conflict(s) with other Follow-up Payment Plan(s).']"
        self.assertEqual(self.payment_plan.exclude_household_error, error_msg)

    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_exclude_successfully(self, get_exchange_rate_mock: Any) -> None:
        self.payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
        self.payment_plan.save(update_fields=["background_action_status"])

        hh_unicef_id_1 = Household.objects.get(id=self.household_1.id).unicef_id
        hh_unicef_id_2 = Household.objects.get(id=self.household_2.id).unicef_id

        self.assertEqual(self.payment_plan.exclusion_reason, "")

        payment_plan_exclude_beneficiaries(
            payment_plan_id=self.payment_plan.pk,
            excluding_hh_ids=[hh_unicef_id_1, hh_unicef_id_2],
            exclusion_reason="Nice Job!",
        )

        self.payment_plan.refresh_from_db()

        self.assertEqual(self.payment_plan.exclusion_reason, "Nice Job!")
        self.assertEqual(self.payment_plan.exclude_household_error, "")
        self.assertEqual(self.payment_plan.background_action_status, None)

        # excluded hh_1, hh_2
        self.assertEqual(set(self.payment_plan.excluded_households_ids), {hh_unicef_id_1, hh_unicef_id_2})
