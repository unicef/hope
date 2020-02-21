from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea


class TestCreateProgram(APITestCase):
    CREATE_PROGRAM_MUTATION = """
    mutation CreateProgram($programData: CreateProgramInput!) {
      createProgram(programData: $programData) {
        program {
          name
          status
          startDate
          endDate
          programCaId
          budget
          description
          frequencyOfPayments
          sector
          scope
          cashPlus
          populationGoal
          administrativeAreasOfImplementation
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.program_data = {
            "programData": {
                "name": "Test",
                "startDate": "2019-12-20",
                "endDate": "2021-12-20",
                "programCaId": "5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3",
                "budget": 20000000,
                "description": "my description of program",
                "frequencyOfPayments": "REGULAR",
                "sector": "EDUCATION",
                "scope": "FULL",
                "cashPlus": True,
                "populationGoal": 150000,
                "administrativeAreasOfImplementation": "Lorem Ipsum",
                "businessAreaSlug":  BusinessArea.objects.order_by("?").first().slug,
            }
        }

    def test_create_program_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            variables=self.program_data
        )

    def test_create_program_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.program_data
        )

    def test_create_program_invalid_dates(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.program_data
        )
