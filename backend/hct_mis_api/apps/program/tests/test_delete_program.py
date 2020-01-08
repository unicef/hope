from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.tests import APITestCase
from program.models import Program


class TestDeleteProgram(APITestCase):
    DELETE_PROGRAM_MUTATION = """
    mutation DeleteProgram($programId: String!) {
      deleteProgram(programId: $programId) {
            ok
      }
    }
    """

    def test_delete_program_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            variables={
                "programId": "UHJvZ3JhbU5vZGU6MDBkMmU4ZWQtOThm"
                             "My00YTM5LWJiZWYtZmI5YWUwNWYyOThh"
            },
        )

    def test_delete_program_authenticated(self):
        user = UserFactory.create()
        location = LocationFactory.create()

        program = Program.objects.create(
            name="Test",
            status="DRAFT",
            start_date="2019-12-20T15:00:00",
            end_date="2021-12-20T15:00:00",
            location_id=location.id,
            program_ca_id="5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3",
            budget=20000000,
            description="my description of program"
        )

        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            context={'user': user},
            variables={
                "programId": self.id_to_base64(program.id, 'program')
            },
        )
