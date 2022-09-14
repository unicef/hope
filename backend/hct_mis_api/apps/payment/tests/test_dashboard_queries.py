import datetime

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.payment.fixtures import CashPlanFactory, PaymentRecordFactory, PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import GenericPayment
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory


class TestDashboardQueries(APITestCase):
    QUERY_SECTION = """
    query {query_name}(
        $businessAreaSlug: String!
        $year: Int!
        $program: String
        $administrativeArea: String
      ) {{
        {query_name}(
          businessAreaSlug: $businessAreaSlug
          year: $year
          program: $program
          administrativeArea: $administrativeArea
        ) {{
          total
        }}
      }}
    """

    QUERY_CHART = """
    query {query_name}(
        $businessAreaSlug: String!
        $year: Int!
        $program: String
        $administrativeArea: String
      ) {{
        {query_name}(
          businessAreaSlug: $businessAreaSlug
          year: $year
          program: $program
          administrativeArea: $administrativeArea
        ) {{
          labels
          datasets {{
            data
          }}
        }}
      }}
    """

    QUERY_TABLE_TOTAL_CASH_TRANSFERRED_BY_ADMINISTRATIVE_AREA = """
    query tableTotalCashTransferredByAdministrativeArea(
        $businessAreaSlug: String!
        $year: Int!
      ) {
        tableTotalCashTransferredByAdministrativeArea(
          businessAreaSlug: $businessAreaSlug
          year: $year
        ) {
          data {
            admin2
            totalCashTransferred
            totalHouseholds
          }
        }
      }
    """

    QUERY_CHART_TOTAL_TRANSFERRED_BY_COUNTRY = """
    query chartTotalTransferredCashByCountry(
        $year: Int!
      ) {
        chartTotalTransferredCashByCountry(
          year: $year
        ) {
          labels
          datasets {
            data
            label
          }
        }
      }
    """

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        call_command("loadcountries")
        cls.user = UserFactory()

        chosen_business_areas = ("afghanistan", "botswana", "angola")
        for idx, business_area_slug in enumerate(chosen_business_areas):
            country = geo_models.Country.objects.get(name=business_area_slug.capitalize())
            area_type = AreaTypeFactory(
                name="City",
                country=country,
                area_level=2,
            )
            admin_area1 = AreaFactory(
                name=f"{business_area_slug} city 1", area_type=area_type, p_code=f"{business_area_slug} 1"
            )
            admin_area2 = AreaFactory(
                name=f"{business_area_slug} city 2", area_type=area_type, p_code=f"{business_area_slug} 2"
            )
            admin_area3 = AreaFactory(
                name=f"{business_area_slug} city 3", area_type=area_type, p_code=f"{business_area_slug} 3"
            )

            business_area = BusinessArea.objects.get(slug=business_area_slug)
            cls.create_user_role_with_permissions(cls.user, [Permissions.DASHBOARD_VIEW_COUNTRY], business_area)

            household1, individuals1 = create_household(
                household_args={"size": 2, "business_area": business_area, "admin_area": admin_area1},
            )
            household2, individuals2 = create_household(
                household_args={"size": 2, "business_area": business_area, "admin_area": admin_area2},
            )
            household3, individuals3 = create_household(
                household_args={"size": 2, "business_area": business_area, "admin_area": admin_area3},
            )
            household4, individuals4 = create_household(
                household_args={"size": 2, "business_area": business_area, "admin_area": admin_area1},
            )
            household5, individuals5 = create_household(
                household_args={"size": 2, "business_area": business_area, "admin_area": admin_area2},
            )
            household6, individuals6 = create_household(
                household_args={"size": 2, "business_area": business_area, "admin_area": admin_area3},
            )

            program1 = ProgramFactory.create(cash_plus=True)
            cash_plan1 = CashPlanFactory(program=program1, business_area=business_area)
            PaymentRecordFactory(
                parent=cash_plan1,
                delivery_date=datetime.date(2021, 10, 10),
                household=household1,
                delivery_type=GenericPayment.DELIVERY_TYPE_CASH,
                delivered_quantity_usd=10 + idx,
                status=GenericPayment.STATUS_SUCCESS,
                business_area=business_area,
            )
            PaymentRecordFactory(
                parent=cash_plan1,
                delivery_date=datetime.date(2021, 10, 10),
                household=household2,
                delivery_type=GenericPayment.DELIVERY_TYPE_VOUCHER,
                delivered_quantity_usd=20 + idx,
                status=GenericPayment.STATUS_SUCCESS,
                business_area=business_area,
            )
            PaymentRecordFactory(
                parent=cash_plan1,
                delivery_date=datetime.date(2021, 11, 10),
                household=household3,
                delivery_type=GenericPayment.DELIVERY_TYPE_CASH,
                delivered_quantity_usd=30 + idx,
                status=GenericPayment.STATUS_ERROR,
                business_area=business_area,
            )

            payment_plan1 = PaymentPlanFactory(program=program1, business_area=business_area)
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=datetime.date(2021, 10, 10),
                delivery_type=GenericPayment.DELIVERY_TYPE_CASH,
                delivered_quantity_usd=10 + idx,
                status=GenericPayment.STATUS_SUCCESS,
                business_area=business_area,
                household=household4,
            )
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=datetime.date(2021, 10, 10),
                delivery_type=GenericPayment.DELIVERY_TYPE_VOUCHER,
                delivered_quantity_usd=20 + idx,
                status=GenericPayment.STATUS_SUCCESS,
                business_area=business_area,
                household=household5,
            )
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=datetime.date(2021, 11, 10),
                delivery_type=GenericPayment.DELIVERY_TYPE_CASH,
                delivered_quantity_usd=30 + idx,
                status=GenericPayment.STATUS_ERROR,
                business_area=business_area,
                household=household6,
            )

    @parameterized.expand(
        [
            ("chartVolumeByDeliveryMechanism",),
            ("chartPayment",),
        ]
    )
    def test_charts(self, query_name):
        self.snapshot_graphql_request(
            request_string=self.QUERY_CHART.format(query_name=query_name),
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )

    def test_chart_total_transferred_by_country(self):
        business_area = BusinessArea.objects.get(slug="global")
        self.create_user_role_with_permissions(self.user, [Permissions.DASHBOARD_VIEW_COUNTRY], business_area)
        self.snapshot_graphql_request(
            request_string=self.QUERY_CHART_TOTAL_TRANSFERRED_BY_COUNTRY,
            variables={"year": 2021},
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("sectionTotalTransferred",),
        ]
    )
    def test_sections(self, query_name):
        self.snapshot_graphql_request(
            request_string=self.QUERY_SECTION.format(query_name=query_name),
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )

    def test_table_total_cash_transferred_by_administrative_area(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_TABLE_TOTAL_CASH_TRANSFERRED_BY_ADMINISTRATIVE_AREA,
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )
