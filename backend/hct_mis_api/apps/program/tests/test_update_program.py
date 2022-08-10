from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestUpdateProgram(APITestCase):
    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput, $version: BigInt) {
      updateProgram(programData: $programData, version: $version) {
        program {
          name
          status
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory.create(name="initial name", status=Program.DRAFT, business_area=cls.business_area)

    def test_update_program_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.ACTIVE,
                },
                "version": self.program.version,
            },
        )

    @parameterized.expand(
        [
            ("with_permissions", [Permissions.PROGRAMME_UPDATE, Permissions.PROGRAMME_ACTIVATE], True),
            (
                "with_partial_permissions",
                [
                    Permissions.PROGRAMME_UPDATE,
                ],
                False,
            ),
            ("without_permissions", [], False),
        ]
    )
    def test_update_program_authenticated(self, _, permissions, should_be_updated):
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                    "status": Program.ACTIVE,
                },
                "version": self.program.version,
            },
        )

        updated_program = Program.objects.get(id=self.program.id)
        if should_be_updated:
            assert updated_program.status == Program.ACTIVE
            assert updated_program.name == "updated name"
        else:
            assert updated_program.status == Program.DRAFT
            assert updated_program.name == "initial name"
