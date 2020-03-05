from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea
from household.fixtures import IndividualFactory, HouseholdFactory
from program.fixtures import ProgramFactory


class TestIndividualQuery(APITestCase):
    ALL_INDIVIDUALS_QUERY = """
    query AllIndividuals {
      allIndividuals {
        edges {
          node {
            fullName
            firstName
            lastName
            phoneNumber
            dob
          }
        }
      }
    }
    """
    ALL_INDIVIDUALS_BY_PROGRAMME_QUERY = """
    query AllIndividuals {
      allIndividuals(programme: "Test program TWO") {
        edges {
          node {
            fullName
            firstName
            lastName
            phoneNumber
            dob
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
        firstName
        lastName
        phoneNumber
        dob
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory()
        program_one = ProgramFactory(
            name="Test program ONE", business_area=BusinessArea.objects.first(),
        )
        program_two = ProgramFactory(
            name="Test program TWO", business_area=BusinessArea.objects.first(),
        )
        household_one = HouseholdFactory()
        household_two = HouseholdFactory()
        household_one.programs.add(program_one)
        household_two.programs.add(program_two)

        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "first_name": "Benjamin",
                "last_name": "Butler",
                "phone_number": "(953)682-4596",
                "dob": "1943-07-30",
            },
            {
                "full_name": "Robin Ford",
                "first_name": "Robin",
                "last_name": "Ford",
                "phone_number": "+18663567905",
                "dob": "1946-02-15",
            },
            {
                "full_name": "Timothy Perry",
                "first_name": "Timothy",
                "last_name": "Perry",
                "phone_number": "(548)313-1700-902",
                "dob": "1983-12-21",
            },
            {
                "full_name": "Eric Torres",
                "first_name": "Eric",
                "last_name": "Torres",
                "phone_number": "(228)231-5473",
                "dob": "1973-03-23",
            },
            {
                "full_name": "Jenna Franklin",
                "first_name": "Jenna",
                "last_name": "Franklin",
                "phone_number": "001-296-358-5428-607",
                "dob": "1969-11-29",
            },
        ]

        self.individuals = [
            IndividualFactory(
                household=household_one if index % 2 else household_two,
                **individual
            )
            for index, individual in enumerate(self.individuals_to_create)
        ]

    def test_individual_query_all(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={"user": self.user},
        )

    def test_individual_query_single(self):
        self.snapshot_graphql_request(
            request_string=self.INDIVIDUAL_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(self.individuals[0].id, "Individual")
            },
        )

    def test_individual_programme_filter(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_BY_PROGRAMME_QUERY,
            context={"user": self.user},
        )
