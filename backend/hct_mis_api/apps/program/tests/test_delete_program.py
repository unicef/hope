from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea
from program.fixtures import ProgramFactory


class TestDeleteProgram(APITestCase):
    DELETE_PROGRAM_MUTATION = """
    mutation DeleteProgram($programId: String!) {
      deleteProgram(programId: $programId) {
            ok
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()

    def test_delete_program_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            variables={
                "programId": "UHJvZ3JhbU5vZGU6MDBkMmU4ZWQtOThm"
                "My00YTM5LWJiZWYtZmI5YWUwNWYyOThh"
            },
        )

    def test_delete_program_authenticated(self):
        program_draft = ProgramFactory.create(
            status="DRAFT",
            business_area=BusinessArea.objects.order_by("?").first(),
        )

        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programId": self.id_to_base64(program_draft.id, "Program")
            },
        )

    def test_delete_active_program(self):
        program_active = ProgramFactory.create(
            status="ACTIVE",
            business_area=BusinessArea.objects.order_by("?").first(),
        )

        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programId": self.id_to_base64(program_active.id, "Program")
            },
        )
