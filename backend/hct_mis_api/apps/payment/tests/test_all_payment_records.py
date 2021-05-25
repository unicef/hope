from datetime import datetime

from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory


class TestAllPaymentRecords(APITestCase):
    ALL_PAYMENT_RECORDS_QUERY = """
    query AllPaymentRecords($cashPlan: ID, $household: ID, $businessArea: String) {
      allPaymentRecords(cashPlan: $cashPlan, household: $household, businessArea: $businessArea) {
        totalCount
        edgeCount
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        (self.household1, _) = create_household(household_args={"size": 1})
        (self.household2, _) = create_household(household_args={"size": 1})
        (self.household3, _) = create_household(household_args={"size": 1})
        business_area = BusinessArea.objects.get(slug="afghanistan")
        PaymentRecordFactory.create_batch(
            3,
            business_area=business_area,
            household=self.household1,
        )
        PaymentRecordFactory.create_batch(
            4,
            business_area=business_area,
            household=self.household2,
        )
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS],
            BusinessArea.objects.get(slug="afghanistan")
        )

    def test_fetch_payment_records_only_for_single_household(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENT_RECORDS_QUERY,
            context={"user": self.user},
            variables={
                "household": self.household1.pk,
                "businessArea": "afghanistan",
                "first": 5,
            }
        )

    def test_household_without_payment_records_should_return_empty_list(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENT_RECORDS_QUERY,
            context={"user": self.user},
            variables={
                "household": self.household3.pk,
                "businessArea": "afghanistan",
                "first": 5,
            }
        )
