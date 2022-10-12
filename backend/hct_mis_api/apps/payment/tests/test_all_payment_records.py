import itertools

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import CashPlanFactory, PaymentRecordFactory


class TestAllPaymentRecords(APITestCase):
    ALL_PAYMENT_RECORDS_QUERY = """
    query AllPaymentRecords($cashPlan: ID, $household: ID, $businessArea: String) {
      allPaymentRecords(parent: $cashPlan, household: $household, businessArea: $businessArea) {
        totalCount
        edgeCount
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        (cls.household1, _) = create_household(household_args={"size": 1})
        (cls.household2, _) = create_household(household_args={"size": 1})
        (cls.household3, _) = create_household(household_args={"size": 1})
        business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.cash_plan1 = CashPlanFactory(funds_commitment="123456", exchange_rate=None)
        cls.cash_plan2 = CashPlanFactory(funds_commitment="123456", exchange_rate=None)
        cls.cash_plan3 = CashPlanFactory(funds_commitment="123456", exchange_rate=None)
        PaymentRecordFactory.create_batch(
            2,
            business_area=business_area,
            household=cls.household1,
            parent=cls.cash_plan1,
        )
        PaymentRecordFactory.create_batch(
            1,
            business_area=business_area,
            household=cls.household1,
            parent=cls.cash_plan2,
        )
        PaymentRecordFactory.create_batch(
            2,
            business_area=business_area,
            household=cls.household2,
            parent=cls.cash_plan1,
        )
        PaymentRecordFactory.create_batch(
            2,
            business_area=business_area,
            household=cls.household2,
            parent=cls.cash_plan3,
        )
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS], BusinessArea.objects.get(slug="afghanistan")
        )

    def test_fetch_payment_records_filter_by_household(self):
        for household in [self.household1, self.household2, self.household3]:
            self.snapshot_graphql_request(
                request_string=self.ALL_PAYMENT_RECORDS_QUERY,
                context={"user": self.user},
                variables={
                    "household": encode_id_base64(household.pk, "Household"),
                    "businessArea": "afghanistan",
                },
            )

    def test_fetch_payment_records_filter_by_cash_plan(self):
        for cash_plan in [self.cash_plan1, self.cash_plan2, self.cash_plan3]:
            self.snapshot_graphql_request(
                request_string=self.ALL_PAYMENT_RECORDS_QUERY,
                context={"user": self.user},
                variables={
                    "cashPlan": encode_id_base64(cash_plan.pk, "CashPlan"),
                    "businessArea": "afghanistan",
                },
            )

    def test_fetch_payment_records_filter_by_cash_plan_and_household(self):
        households = [self.household1, self.household2, self.household3]
        cash_plans = [self.cash_plan1, self.cash_plan2, self.cash_plan3]
        for household, cash_plan in itertools.product(households, cash_plans):
            self.snapshot_graphql_request(
                request_string=self.ALL_PAYMENT_RECORDS_QUERY,
                context={"user": self.user},
                variables={
                    "household": encode_id_base64(household.pk, "Household"),
                    "cashPlan": encode_id_base64(cash_plan.pk, "CashPlan"),
                    "businessArea": "afghanistan",
                },
            )
