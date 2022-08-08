from datetime import datetime
from django.utils import timezone

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory, CashPlanFactory
from hct_mis_api.apps.payment.models import PaymentRecord


class TestChartTotalTransferredCashByCountry(APITestCase):
    CHART_TOTAL_TRANSFERRED_CASH_BY_COUNTRY_QUERY = """
    query ChartTotalTransferredCashByCountry($year: Int!) {
      chartTotalTransferredCashByCountry(year: $year) {
        datasets {
          data
          label
        }
        labels
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        cls.user = UserFactory.create()
        (household, _) = create_household(household_args={"size": 1})
        cash_plan = CashPlanFactory(funds_commitment="123456", exchange_rate=None)
        chosen_business_areas = ("afghanistan", "botswana", "angola")
        for business_area_slug in chosen_business_areas:
            business_area = BusinessArea.objects.get(slug=business_area_slug)
            PaymentRecordFactory.create_batch(
                3,
                delivery_date=timezone.make_aware(datetime(year=2021, day=1, month=1)),
                business_area=business_area,
                delivery_type=PaymentRecord.DELIVERY_TYPE_CASH,
                delivered_quantity_usd=200.20,
                cash_plan=cash_plan,
                household=household,
            )
            PaymentRecordFactory.create_batch(
                3,
                delivery_date=timezone.make_aware(datetime(year=2021, day=1, month=1)),
                business_area=business_area,
                delivery_type=PaymentRecord.DELIVERY_TYPE_VOUCHER,
                delivered_quantity_usd=100.00,
                cash_plan=cash_plan,
                household=household,
            )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.DASHBOARD_VIEW_COUNTRY],
            ),
            ("without_permission", []),
        ]
    )
    def test_resolving_chart(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, BusinessArea.objects.get(slug="global"))

        self.snapshot_graphql_request(
            request_string=self.CHART_TOTAL_TRANSFERRED_CASH_BY_COUNTRY_QUERY,
            context={"user": self.user},
            variables={"year": 2021},
        )
