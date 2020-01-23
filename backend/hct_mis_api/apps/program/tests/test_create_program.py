from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.base_test_case import APITestCase


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
        self.user = UserFactory.create()
        location = LocationFactory.create()
        self.location_id = self.id_to_base64(location.id, "Location")

    def test_create_program_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            variables={
                "programData": {
                    "name": "Test",
                    "startDate": "2019-12-20T15:00:00",
                    "endDate": "2021-12-20T15:00:00",
                    "locationId": "TG9jYXRpb25Ob2RlOjhiNGM2YmJhLWJmN"
                    "WMtNDIyNC04Yjc0LTZlMTAwOTVkNDRlOQ==",
                    "programCaId": "5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3",
                    "budget": 20000000,
                    "description": "my description of program",
                    "frequencyOfPayments": "REGULAR",
                    "sector": "EDUCATION",
                    "scope": "FULL",
                    "cashPlus": True,
                    "populationGoal": 150000,
                }
            },
        )

    def test_create_program_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "name": "Test",
                    "startDate": "2019-12-20T15:00:00",
                    "endDate": "2021-12-20T15:00:00",
                    "locationId": self.location_id,
                    "programCaId": "5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3",
                    "budget": 20000000,
                    "description": "my description of program",
                    "frequencyOfPayments": "REGULAR",
                    "sector": "EDUCATION",
                    "scope": "FULL",
                    "cashPlus": True,
                    "populationGoal": 150000,
                    "administrativeAreasOfImplementation": "Lorem Ipsum",
                }
            },
        )

    def test_create_program_invalid_dates(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "name": "Test",
                    "startDate": "2023-12-20T15:00:00",
                    "endDate": "2021-12-20T15:00:00",
                    "locationId": self.location_id,
                    "programCaId": "5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3",
                    "budget": 20000000,
                    "description": "my description of program",
                    "frequencyOfPayments": "REGULAR",
                    "sector": "EDUCATION",
                    "scope": "FULL",
                    "cashPlus": True,
                    "populationGoal": 150000,
                    "administrativeAreasOfImplementation": "Lorem Ipsum",
                }
            },
        )
