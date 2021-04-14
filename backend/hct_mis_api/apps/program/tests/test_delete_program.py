from django.core.management import call_command
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


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
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.program = ProgramFactory.create(status=Program.DRAFT, business_area=self.business_area)

    def test_delete_program_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            variables={"programId": self.id_to_base64(self.program.id, "ProgramNode")},
        )

    @parameterized.expand(
        [
            ("with_permission_in_draft", [Permissions.PROGRAMME_REMOVE], Program.DRAFT),
            ("without_permission_in_draft", [], Program.DRAFT),
            ("with_permission_in_active", [Permissions.PROGRAMME_REMOVE], Program.ACTIVE),
        ]
    )
    def test_delete_program_authenticated(self, _, permissions, status):
        user = UserFactory.create()

        self.create_user_role_with_permissions(user, permissions, self.business_area)
        self.program.status = status
        self.program.save()

        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            context={"user": user},
            variables={"programId": self.id_to_base64(self.program.id, "ProgramNode")},
        )
