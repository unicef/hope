from django.utils import timezone

from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentRecordFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

QUERY_CHART_PROGRAMMES_BY_SECTOR = """
query chartProgrammesBySector(
    $businessAreaSlug: String!
    $year: Int!
    $program: String
    $administrativeArea: String
  ) {
    chartProgrammesBySector(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      labels
      datasets {
        label
        data
      }
    }
  }
"""


QUERY_CHART_TOTAL_TRANSFERRED_BY_MONTH = """
query chartTotalTransferredByMonth(
    $businessAreaSlug: String!
    $year: Int!
    $program: String
    $administrativeArea: String
  ) {
    chartTotalTransferredByMonth(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      labels
      datasets {
        label
        data
      }
    }
  }
"""


class TestDashboardQueries(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory()
        cls.create_user_role_with_permissions(cls.user, [Permissions.DASHBOARD_VIEW_COUNTRY], cls.business_area)
        generate_delivery_mechanisms()

    def test_chart_programmes_by_sector(self) -> None:
        household, individuals = create_household(
            household_args={"size": 2, "business_area": self.business_area},
        )
        program1 = ProgramFactory.create(cash_plus=True, sector=Program.EDUCATION)
        program2 = ProgramFactory.create(cash_plus=False, sector=Program.HEALTH)
        program3 = ProgramFactory.create(cash_plus=False, sector=Program.NUTRITION)
        program4 = ProgramFactory.create(cash_plus=True, sector=Program.WASH)

        cash_plan1 = CashPlanFactory(program=program1)
        cash_plan2 = CashPlanFactory(program=program2)
        delivery_date = timezone.datetime(2021, 10, 10, tzinfo=utc)
        PaymentRecordFactory(parent=cash_plan1, delivery_date=delivery_date, household=household, currency="PLN")
        PaymentRecordFactory(parent=cash_plan2, delivery_date=delivery_date, household=household, currency="PLN")

        payment_plan1 = PaymentPlanFactory(program=program3)
        payment_plan2 = PaymentPlanFactory(program=program4)
        PaymentFactory(parent=payment_plan1, delivery_date=delivery_date, household=household, currency="PLN")
        PaymentFactory(parent=payment_plan2, delivery_date=delivery_date, household=household, currency="PLN")

        self.snapshot_graphql_request(
            request_string=QUERY_CHART_PROGRAMMES_BY_SECTOR,
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )

    def test_chart_total_transferred_by_month(self) -> None:
        dm_cash = DeliveryMechanism.objects.get(code="cash")
        dm_voucher = DeliveryMechanism.objects.get(code="voucher")
        household, individuals = create_household(
            household_args={"size": 2, "business_area": self.business_area},
        )
        program1 = ProgramFactory.create(cash_plus=True, sector=Program.EDUCATION)
        cash_plan1 = CashPlanFactory(program=program1)
        delivery_date1 = timezone.datetime(2021, 10, 10, tzinfo=utc)
        delivery_date2 = timezone.datetime(2021, 11, 10, tzinfo=utc)
        PaymentRecordFactory(
            parent=cash_plan1,
            delivery_date=delivery_date1,
            household=household,
            delivery_type=dm_cash,
            delivered_quantity_usd=133,
            currency="PLN",
        )
        PaymentRecordFactory(
            parent=cash_plan1,
            delivery_date=delivery_date1,
            household=household,
            delivery_type=dm_voucher,
            delivered_quantity_usd=25,
            currency="PLN",
        )
        PaymentRecordFactory(
            parent=cash_plan1,
            delivery_date=delivery_date2,
            household=household,
            delivery_type=dm_cash,
            delivered_quantity_usd=133,
            currency="PLN",
        )
        PaymentRecordFactory(
            parent=cash_plan1,
            delivery_date=delivery_date2,
            household=household,
            delivery_type=dm_voucher,
            delivered_quantity_usd=25,
            currency="PLN",
        )

        payment_plan1 = PaymentPlanFactory(program=program1)
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=delivery_date1,
            delivery_type=dm_cash,
            delivered_quantity_usd=133,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=delivery_date1,
            delivery_type=dm_voucher,
            delivered_quantity_usd=25,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=delivery_date2,
            delivery_type=dm_cash,
            delivered_quantity_usd=133,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=delivery_date2,
            delivery_type=dm_voucher,
            delivered_quantity_usd=25,
            currency="PLN",
        )

        self.snapshot_graphql_request(
            request_string=QUERY_CHART_TOTAL_TRANSFERRED_BY_MONTH,
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )
