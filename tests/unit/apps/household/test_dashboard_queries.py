from django.utils import timezone

from parameterized import parameterized
from pytz import utc

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from tests.extras.test_utils.factories.account import UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory


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

    QUERY_CHART_REACHED_BY_AGE_AND_GENDER = """
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

    QUERY_CHART_WITH_DISABILITY_REACHED_BY_AGE = """
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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
                "size": 15,
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
                "size": 15,
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
                "size": 5,
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
                "size": 5,
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
        payment_plan1 = PaymentPlanFactory(program_cycle=cls.program_one.cycles.first())
        delivery_date = timezone.datetime(2021, 10, 10, tzinfo=utc)
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=delivery_date,
            household=household1,
            delivered_quantity_usd=100,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=delivery_date,
            household=household2,
            delivered_quantity_usd=100,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=delivery_date,
            household=household3,
            delivered_quantity_usd=100,
            currency="PLN",
        )

        payment_plan2 = PaymentPlanFactory(program_cycle=cls.program_two.cycles.first())
        PaymentFactory(
            parent=payment_plan2,
            delivery_date=delivery_date,
            delivered_quantity_usd=100,
            household=household1,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan2,
            delivery_date=delivery_date,
            delivered_quantity_usd=100,
            household=household2,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan2,
            delivery_date=delivery_date,
            delivered_quantity_usd=100,
            household=household4,
            currency="PLN",
        )

    @parameterized.expand(
        [
            ("sectionHouseholdsReached",),
            ("sectionIndividualsReached",),
            ("sectionChildReached",),
            ("sectionPeopleReached",),
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
            ("chartIndividualsReachedByAgeAndGender",),
            ("chartPeopleReachedByAgeAndGender",),
        ]
    )
    def test_charts_reached_by_age_and_gender(self, query_name: str) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_CHART_REACHED_BY_AGE_AND_GENDER.format(query_name=query_name),
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("chartIndividualsWithDisabilityReachedByAge",),
            ("chartPeopleWithDisabilityReachedByAge",),
        ]
    )
    def test_charts_individuals_with_disability_reached_by_age(self, query_name: str) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_CHART_WITH_DISABILITY_REACHED_BY_AGE.format(query_name=query_name),
            variables={"businessAreaSlug": "afghanistan", "year": 2021},
            context={"user": self.user},
        )
