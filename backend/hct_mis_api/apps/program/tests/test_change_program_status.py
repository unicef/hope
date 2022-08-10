from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


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

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.user = UserFactory.create()

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="State",
            country=country,
            area_level=1,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

    @parameterized.expand(
        [
            ("draft_to_active_with_permission", [Permissions.PROGRAMME_ACTIVATE], Program.DRAFT, Program.ACTIVE),
            ("draft_to_acive_without_permission", [Permissions.PROGRAMME_FINISH], Program.DRAFT, Program.ACTIVE),
            ("finish_to_active_with_permission", [Permissions.PROGRAMME_ACTIVATE], Program.FINISHED, Program.ACTIVE),
            ("finish_to_active_without_permission", [], Program.FINISHED, Program.ACTIVE),
            ("draft_to_finished_with_permission", [Permissions.PROGRAMME_FINISH], Program.DRAFT, Program.FINISHED),
            ("draft_to_finished_without_permission", [], Program.DRAFT, Program.FINISHED),
            ("active_to_finished_with_permission", [Permissions.PROGRAMME_FINISH], Program.ACTIVE, Program.FINISHED),
            (
                "active_to_finished_without_permission",
                [Permissions.PROGRAMME_ACTIVATE],
                Program.ACTIVE,
                Program.FINISHED,
            ),
            (
                "active_to_draft",
                [Permissions.PROGRAMME_ACTIVATE, Permissions.PROGRAMME_FINISH, Permissions.PROGRAMME_UPDATE],
                Program.ACTIVE,
                Program.DRAFT,
            ),
            (
                "finished_to_draft",
                [Permissions.PROGRAMME_ACTIVATE, Permissions.PROGRAMME_FINISH, Permissions.PROGRAMME_UPDATE],
                Program.FINISHED,
                Program.DRAFT,
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
