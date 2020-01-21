from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from program.fixtures import ProgramFactory


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
        program = ProgramFactory.create()

        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            context={"user": user},
            variables={"programId": self.id_to_base64(program.id, "Program")},
        )
