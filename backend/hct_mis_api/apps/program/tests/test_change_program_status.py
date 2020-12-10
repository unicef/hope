from django.core.management import call_command
from parameterized import parameterized

from account.fixtures import UserFactory
from account.permissions import Permissions
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaFactory, AdminAreaTypeFactory
from core.models import BusinessArea
from program.fixtures import ProgramFactory


class TestChangeProgramStatus(APITestCase):
    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput) {
      updateProgram(programData: $programData) {
        program {
          status
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()

        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        state_area_type = AdminAreaTypeFactory(name="State", business_area=self.business_area, admin_level=1)
        self.admin_area = AdminAreaFactory(admin_area_type=state_area_type)

    @parameterized.expand(
        [
            ("draft_to_active_with_permission", [Permissions.PROGRAMME_ACTIVATE], "DRAFT", "ACTIVE"),
            ("draft_to_acive_without_permission", [Permissions.PROGRAMME_FINISH], "DRAFT", "ACTIVE"),
            ("finish_to_active_with_permission", [Permissions.PROGRAMME_ACTIVATE], "FINISHED", "ACTIVE"),
            ("finish_to_active_without_permission", [], "FINISHED", "ACTIVE"),
            ("draft_to_finished_with_permission", [Permissions.PROGRAMME_FINISH], "DRAFT", "FINISHED"),
            ("draft_to_finished_without_permission", [], "DRAFT", "FINISHED"),
            ("active_to_finished_with_permission", [Permissions.PROGRAMME_FINISH], "ACTIVE", "FINISHED"),
            ("active_to_finished_without_permission", [Permissions.PROGRAMME_ACTIVATE], "ACTIVE", "FINISHED"),
            (
                "active_to_draft",
                [Permissions.PROGRAMME_ACTIVATE, Permissions.PROGRAMME_FINISH, Permissions.PROGRAMME_UPDATE],
                "ACTIVE",
                "DRAFT",
            ),
            (
                "finished_to_draft",
                [Permissions.PROGRAMME_ACTIVATE, Permissions.PROGRAMME_FINISH, Permissions.PROGRAMME_UPDATE],
                "FINISHED",
                "DRAFT",
            ),
        ]
    )
    def test_status_change(self, _, permissions, initial_status, target_status):
        program = ProgramFactory.create(
            status=initial_status,
            business_area=self.business_area,
        )

        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={"programData": {"id": self.id_to_base64(program.id, "ProgramNode"), "status": target_status}},
        )
