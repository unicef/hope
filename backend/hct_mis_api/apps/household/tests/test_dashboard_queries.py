import datetime

from parameterized import parameterized

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
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


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

    QUERY_chartIndividualsReachedByAgeAndGender = """
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

    QUERY_chartIndividualsWithDisabilityReachedByAge = """
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
            label
            data
          }}
        }}
      }}
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory()
        cls.create_user_role_with_permissions(cls.user, [Permissions.DASHBOARD_VIEW_COUNTRY], cls.business_area)

        cls.program_one = ProgramFactory(
            name="Test program ONE",
            business_area=cls.business_area,
        )
        cls.program_two = ProgramFactory(
            name="Test program TWO",
            business_area=cls.business_area,
        )

        household1, individuals1 = create_household(
            household_args={
                "size": 2,
                "business_area": cls.business_area,
                "female_age_group_0_5_disabled_count": 2,
                "male_age_group_60_disabled_count": 2,
                "female_age_group_0_5_count": 4,
                "female_age_group_6_11_count": 2,
                "female_age_group_12_17_count": 2,
                "female_age_group_18_59_count": 0,
                "female_age_group_60_count": 2,
                "male_age_group_0_5_count": 0,
                "male_age_group_6_11_count": 0,
                "male_age_group_12_17_count": 0,
                "male_age_group_18_59_count": 2,
                "male_age_group_60_count": 3,
            },
        )
        household2, individuals2 = create_household(
            household_args={
                "size": 2,
                "business_area": cls.business_area,
                "female_age_group_0_5_disabled_count": 2,
                "male_age_group_60_disabled_count": 2,
                "female_age_group_0_5_count": 4,
                "female_age_group_6_11_count": 2,
                "female_age_group_12_17_count": 2,
                "female_age_group_18_59_count": 0,
                "female_age_group_60_count": 2,
                "male_age_group_0_5_count": 0,
                "male_age_group_6_11_count": 0,
                "male_age_group_12_17_count": 0,
                "male_age_group_18_59_count": 2,
                "male_age_group_60_count": 3,
            },
        )
        household3, individuals3 = create_household(
            household_args={
                "size": 2,
                "business_area": cls.business_area,
                "female_age_group_18_59_disabled_count": 1,
                "female_age_group_0_5_count": 0,
                "female_age_group_6_11_count": 0,
                "female_age_group_12_17_count": 0,
                "female_age_group_18_59_count": 2,
                "female_age_group_60_count": 0,
                "male_age_group_0_5_count": 0,
                "male_age_group_6_11_count": 2,
                "male_age_group_12_17_count": 0,
                "male_age_group_18_59_count": 0,
                "male_age_group_60_count": 0,
            },
        )
        household4, individuals4 = create_household(
            household_args={
                "size": 2,
                "business_area": cls.business_area,
                "female_age_group_18_59_disabled_count": 1,
                "female_age_group_0_5_count": 0,
                "female_age_group_6_11_count": 0,
                "female_age_group_12_17_count": 0,
                "female_age_group_18_59_count": 2,
                "female_age_group_60_count": 0,
                "male_age_group_0_5_count": 0,
                "male_age_group_6_11_count": 2,
                "male_age_group_12_17_count": 0,
                "male_age_group_18_59_count": 0,
                "male_age_group_60_count": 0,
            },
        )
        cash_plan1 = CashPlanFactory(program=cls.program_one)
        PaymentRecordFactory(
            parent=cash_plan1,
            delivery_date=datetime.date(2021, 10, 10),
            household=household1,
            delivered_quantity_usd=100,
        )
        PaymentRecordFactory(
            parent=cash_plan1,
            delivery_date=datetime.date(2021, 10, 10),
            household=household2,
            delivered_quantity_usd=100,
        )
        PaymentRecordFactory(
            parent=cash_plan1,
            delivery_date=datetime.date(2021, 10, 10),
            household=household3,
            delivered_quantity_usd=100,
        )

        payment_plan1 = PaymentPlanFactory(program=cls.program_two)
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=datetime.date(2021, 10, 10),
            delivered_quantity_usd=100,
            household=household1,
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=datetime.date(2021, 10, 10),
            delivered_quantity_usd=100,
            household=household2,
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=datetime.date(2021, 10, 10),
            delivered_quantity_usd=100,
            household=household4,
        )

    @parameterized.expand(
        [
            ("sectionHouseholdsReached",),
            ("sectionIndividualsReached",),
            ("sectionChildReached",),
        ]
    )
    def test_sections(self, query_name):
        self.snapshot_graphql_request(
            request_string=self.QUERY_SECTION.format(query_name=query_name),
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("chartIndividualsReachedByAgeAndGender",),
            ("chartIndividualsWithDisabilityReachedByAge",),
        ]
    )
    def test_charts(self, query_name):
        self.snapshot_graphql_request(
            request_string=getattr(self, f"QUERY_{query_name}").format(query_name=query_name),
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )
