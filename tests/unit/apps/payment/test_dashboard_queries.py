import unittest
from decimal import Decimal

from django.core.management import call_command
from django.db.models import Sum
from django.utils import timezone

import pytest
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory
from parameterized import parameterized
from pytz import utc

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.payment.models import DeliveryMechanism, Payment


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
        $orderBy: String
      ) {
        tableTotalCashTransferredByAdministrativeArea(
          businessAreaSlug: $businessAreaSlug
          year: $year
          orderBy: $orderBy
        ) {
          data {
            admin2
            totalCashTransferred
            totalHouseholds
          }
        }
      }
    """

    QUERY_TABLE_TOTAL_CASH_TRANSFERRED_BY_ADMINISTRATIVE_AREA_FOR_PEOPLE = """
    query tableTotalCashTransferredByAdministrativeAreaForPeople(
        $businessAreaSlug: String!
        $year: Int!
        $orderBy: String
      ) {
        tableTotalCashTransferredByAdministrativeAreaForPeople(
          businessAreaSlug: $businessAreaSlug
          year: $year
          orderBy: $orderBy
        ) {
          data {
            admin2
            totalCashTransferred
            totalPeople
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadbusinessareas")
        call_command("loadcountries")
        generate_delivery_mechanisms()
        cls.dm_cash = DeliveryMechanism.objects.get(code="cash")
        cls.dm_voucher = DeliveryMechanism.objects.get(code="voucher")
        cls.user = UserFactory()
        fsp = FinancialServiceProviderFactory()

        chosen_business_areas = (
            ("afghanistan", 100),
            ("angola", 300),
            ("botswana", 200),
        )
        for business_area_slug, num in chosen_business_areas:
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

            program1 = ProgramFactory(
                cash_plus=True,
                start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
                end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
            )

            household1_admin1, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area1,
                    "program": program1,
                },
            )
            household2_admin1, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area1,
                    "program": program1,
                },
            )
            household1_admin2, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area2,
                    "program": program1,
                },
            )
            household2_admin2, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area2,
                    "program": program1,
                },
            )
            household3_admin2, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area2,
                    "program": program1,
                },
            )
            household1_admin3, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area3,
                    "program": program1,
                },
            )
            household2_admin3, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area3,
                    "program": program1,
                },
            )
            household3_admin3, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area3,
                    "program": program1,
                },
            )
            household4_admin3, _ = create_household(
                household_args={
                    "size": 2,
                    "business_area": business_area,
                    "admin_area": admin_area3,
                    "program": program1,
                },
            )
            payment_plan1 = PaymentPlanFactory(program_cycle=program1.cycles.first(), business_area=business_area)
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
                household=household1_admin1,
                delivery_type=cls.dm_cash,
                delivered_quantity=10 + num,
                delivered_quantity_usd=10 + num,
                status=Payment.STATUS_SUCCESS,
                business_area=business_area,
                currency="PLN",
            )
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
                household=household1_admin2,
                delivery_type=cls.dm_voucher,
                delivered_quantity=20 + num,
                delivered_quantity_usd=20 + num,
                status=Payment.STATUS_SUCCESS,
                business_area=business_area,
                currency="PLN",
            )
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
                household=household3_admin2,
                delivery_type=cls.dm_voucher,
                delivered_quantity=20 + num,
                delivered_quantity_usd=20 + num,
                status=Payment.STATUS_SUCCESS,
                business_area=business_area,
                currency="PLN",
            )
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=timezone.datetime(2021, 11, 10, tzinfo=utc),
                household=household1_admin3,
                delivery_type=cls.dm_cash,
                delivered_quantity=30 + num,
                delivered_quantity_usd=30 + num,
                status=Payment.STATUS_ERROR,
                business_area=business_area,
                currency="PLN",
            )
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
                household=household3_admin3,
                delivery_type=cls.dm_voucher,
                delivered_quantity=20 + num,
                delivered_quantity_usd=20 + num,
                status=Payment.STATUS_SUCCESS,
                business_area=business_area,
                currency="PLN",
            )
            PaymentFactory(
                parent=payment_plan1,
                delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
                household=household4_admin3,
                delivery_type=cls.dm_voucher,
                delivered_quantity=20 + num,
                delivered_quantity_usd=20 + num,
                status=Payment.STATUS_SUCCESS,
                business_area=business_area,
                currency="PLN",
            )

            payment_plan2 = PaymentPlanFactory(program_cycle=program1.cycles.first(), business_area=business_area)
            PaymentFactory(
                parent=payment_plan2,
                delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
                delivery_type=cls.dm_cash,
                delivered_quantity=10 + num,
                delivered_quantity_usd=10 + num,
                status=Payment.STATUS_SUCCESS,
                business_area=business_area,
                household=household2_admin1,
                currency="PLN",
                financial_service_provider=fsp,
            )
            PaymentFactory(
                parent=payment_plan2,
                delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
                delivery_type=cls.dm_voucher,
                delivered_quantity=20 + num,
                delivered_quantity_usd=20 + num,
                status=Payment.STATUS_SUCCESS,
                business_area=business_area,
                household=household2_admin2,
                currency="PLN",
                financial_service_provider=fsp,
            )
            PaymentFactory(
                parent=payment_plan2,
                delivery_date=timezone.datetime(2021, 11, 10, tzinfo=utc),
                delivery_type=cls.dm_cash,
                delivered_quantity=30 + num,
                delivered_quantity_usd=30 + num,
                status=Payment.STATUS_ERROR,
                business_area=business_area,
                household=household2_admin3,
                currency="PLN",
                financial_service_provider=fsp,
            )

    @parameterized.expand(
        [
            ("chartVolumeByDeliveryMechanism",),
            ("chartPayment",),
        ]
    )
    def test_charts(self, query_name: str) -> None:
        self.maxDiff = None
        self.snapshot_graphql_request(
            request_string=self.QUERY_CHART.format(query_name=query_name),
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )

    @pytest.mark.xfail(reason="to refactor")
    @unittest.skip("to refactor")
    def test_chart_total_transferred_by_country(self) -> None:
        business_area = BusinessArea.objects.get(slug="global")
        self.create_user_role_with_permissions(self.user, [Permissions.DASHBOARD_VIEW_COUNTRY], business_area)
        response = self.graphql_request(
            request_string=self.QUERY_CHART_TOTAL_TRANSFERRED_BY_COUNTRY,
            variables={"businessAreaSlug": "global", "year": 2021},
            context={"user": self.user},
        )
        resp_data = response["data"]["chartTotalTransferredCashByCountry"]

        for index, ba_name in enumerate(resp_data["labels"]):
            ba = BusinessArea.objects.get(slug=ba_name.lower())
            qs_success_payment_record = Payment.objects.filter(business_area=ba)
            qs_success_payment = Payment.objects.filter(business_area=ba)
            payment_records_cash = qs_success_payment_record.filter(delivery_type=self.dm_cash)
            payment_records_voucher = qs_success_payment_record.filter(delivery_type=self.dm_voucher)
            payments_cash = qs_success_payment.filter(delivery_type=self.dm_cash)
            payments_voucher = qs_success_payment.filter(delivery_type=self.dm_voucher)

            for data_set in resp_data["datasets"]:
                sum1 = sum2 = 0
                if data_set.get("label") == "Actual cash transferred":
                    sum1 = payment_records_cash.aggregate(sum_1=Sum("delivered_quantity_usd"))["sum_1"]
                    sum2 = payments_cash.aggregate(sum_2=Sum("delivered_quantity_usd"))["sum_2"]

                if data_set.get("label") == "Actual voucher transferred":
                    sum1 = payment_records_voucher.aggregate(sum_pr=Sum("delivered_quantity_usd"))["sum_pr"]
                    sum2 = payments_voucher.aggregate(sum_p=Sum("delivered_quantity_usd"))["sum_p"]

                if data_set.get("label") == "Total transferred":
                    sum1 = qs_success_payment_record.aggregate(sum1=Sum("delivered_quantity_usd"))["sum1"]
                    sum2 = qs_success_payment.aggregate(sum2=Sum("delivered_quantity_usd"))["sum2"]

                assert Decimal(data_set["data"][index]) == sum([sum1, sum2])

    @parameterized.expand(
        [
            ("sectionTotalTransferred",),
        ]
    )
    def test_sections(self, query_name: str) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_SECTION.format(query_name=query_name),
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("admin2",),
            ("totalCashTransferred",),
            ("totalHouseholds",),
        ]
    )
    def test_table_total_cash_transferred_by_administrative_area(self, order_by: str) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_TABLE_TOTAL_CASH_TRANSFERRED_BY_ADMINISTRATIVE_AREA,
            variables={"businessAreaSlug": "afghanistan", "year": 2021, "orderBy": order_by},
            context={"user": self.user},
        )

    def test_table_total_cash_transferred_by_administrative_area_for_global_business_area(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_TABLE_TOTAL_CASH_TRANSFERRED_BY_ADMINISTRATIVE_AREA,
            variables={"businessAreaSlug": "global", "year": 2021},
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("admin2",),
            ("totalCashTransferred",),
            ("totalHouseholds",),
        ]
    )
    def test_table_total_cash_transferred_by_administrative_area_for_people(self, order_by: str) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_TABLE_TOTAL_CASH_TRANSFERRED_BY_ADMINISTRATIVE_AREA_FOR_PEOPLE,
            variables={"businessAreaSlug": "afghanistan", "year": 2021, "orderBy": order_by},
            context={"user": self.user},
        )

    def test_table_total_cash_transferred_by_administrative_area_for_people_for_global_business_area(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_TABLE_TOTAL_CASH_TRANSFERRED_BY_ADMINISTRATIVE_AREA_FOR_PEOPLE,
            variables={"businessAreaSlug": "global", "year": 2021},
            context={"user": self.user},
        )
