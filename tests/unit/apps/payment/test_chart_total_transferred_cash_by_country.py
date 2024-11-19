from typing import Any, List

from django.core.management import call_command
from django.utils import timezone

from parameterized import parameterized
from pytz import utc

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentRecordFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism


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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadbusinessareas")
        generate_delivery_mechanisms()
        dm_cash = DeliveryMechanism.objects.get(code="cash")
        dm_voucher = DeliveryMechanism.objects.get(code="voucher")
        cls.partner = PartnerFactory(name="Test1")
        cls.user = UserFactory(partner=cls.partner)
        (household, _) = create_household(household_args={"size": 1})
        cash_plan = CashPlanFactory(funds_commitment="123456", exchange_rate=None)
        chosen_business_areas = ("afghanistan", "botswana", "angola")
        delivery_date = timezone.datetime(2021, 10, 10, tzinfo=utc)
        for business_area_slug in chosen_business_areas:
            business_area = BusinessArea.objects.get(slug=business_area_slug)
            PaymentRecordFactory.create_batch(
                3,
                delivery_date=delivery_date,
                business_area=business_area,
                delivery_type=dm_cash,
                delivered_quantity_usd=200.20,
                parent=cash_plan,
                household=household,
                currency="PLN",
            )
            PaymentRecordFactory.create_batch(
                3,
                delivery_date=delivery_date,
                business_area=business_area,
                delivery_type=dm_voucher,
                delivered_quantity_usd=100.00,
                parent=cash_plan,
                household=household,
                currency="PLN",
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
    def test_resolving_chart(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, BusinessArea.objects.get(slug="global"))

        self.snapshot_graphql_request(
            request_string=self.CHART_TOTAL_TRANSFERRED_CASH_BY_COUNTRY_QUERY,
            context={"user": self.user},
            variables={"year": 2021},
        )
