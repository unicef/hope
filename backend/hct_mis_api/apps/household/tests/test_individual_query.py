import unittest

from django.core.management import call_command
from parameterized import parameterized

from account.fixtures import UserFactory
from account.permissions import Permissions
from core.base_test_case import APITestCase
from core.models import BusinessArea
from household.fixtures import (
    IndividualFactory,
    HouseholdFactory,
)
from program.fixtures import ProgramFactory


class TestIndividualQuery(APITestCase):
    ALL_INDIVIDUALS_QUERY = """
    query AllIndividuals {
      allIndividuals(businessArea: "afghanistan") {
        edges {
          node {
            fullName
            givenName
            familyName
            phoneNo
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
      individual(id: $id) {
        fullName
        givenName
        familyName
        phoneNo
        birthDate
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=self.business_area,
        )
        self.program_two = ProgramFactory(
            name="Test program TWO",
            business_area=self.business_area,
        )

        household_one = HouseholdFactory.build()
        household_two = HouseholdFactory.build()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.save()
        household_one.programs.add(program_one)
        household_two.programs.add(self.program_two)

        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
            },
        ]

        self.individuals = [
            IndividualFactory(household=household_one if index % 2 else household_two, **individual)
            for index, individual in enumerate(self.individuals_to_create)
        ]
        household_one.head_of_household = self.individuals[0]
        household_two.head_of_household = self.individuals[1]
        household_one.save()
        household_two.save()


    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    @unittest.skip("needs adjudication")
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
