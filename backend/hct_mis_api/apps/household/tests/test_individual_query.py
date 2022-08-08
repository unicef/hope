from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import cached_business_areas_slug_id_dict
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestIndividualQuery(APITestCase):
    ALL_INDIVIDUALS_QUERY = """
    query AllIndividuals($search: String) {
      allIndividuals(businessArea: "afghanistan", search: $search, orderBy:"id") {
        edges {
          node {
            fullName
            givenName
            familyName
            phoneNo
            phoneNoValid
            birthDate
          }
        }
      }
    }
    """
    ALL_INDIVIDUALS_BY_PROGRAMME_QUERY = """
    query AllIndividuals($programs: [ID]) {
      allIndividuals(programs: $programs, orderBy: "birth_date", businessArea: "afghanistan") {
        edges {
          node {
            givenName
            familyName
            phoneNo
            birthDate
            household {
              programs {
                edges {
                  node {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    INDIVIDUAL_QUERY = """
    query Individual($id: ID!) {
      individual(id: $id, orderBy:"id") {
        fullName
        givenName
        familyName
        phoneNo
        birthDate
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cls.maxDiff = None
        cached_business_areas_slug_id_dict.cache_clear()
        create_afghanistan()
        cls.user = UserFactory()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=cls.business_area,
        )
        cls.program_two = ProgramFactory(
            name="Test program TWO",
            business_area=cls.business_area,
        )

        household_one = HouseholdFactory.build()
        household_two = HouseholdFactory.build()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.save()
        household_one.programs.add(program_one)
        household_two.programs.add(cls.program_two)

        cls.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "id": "8ef39244-2884-459b-ad14-8d63a6fe4a4a",
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "id": "badd2d2d-7ea0-46f1-bb7a-69f385bacdcd",
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "id": "2c1a26a3-2827-4a99-9000-a88091bf017c",
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "id": "0fc995cc-ea72-4319-9bfe-9c9fda3ec191",
            },
        ]

        cls.individuals = [
            IndividualFactory(household=household_one if index % 2 else household_two, **individual)
            for index, individual in enumerate(cls.individuals_to_create)
        ]
        household_one.head_of_household = cls.individuals[0]
        household_two.head_of_household = cls.individuals[1]
        household_one.save()
        household_two.save()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_individual_query_all(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_individual_query_single(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.INDIVIDUAL_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.individuals[0].id, "IndividualNode")},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_individual_programme_filter(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_BY_PROGRAMME_QUERY,
            context={"user": self.user},
            variables={"programs": [self.program_two.id]},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_filter(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={"user": self.user},
            variables={"search": "001-296-358-5428-607"},
        )
