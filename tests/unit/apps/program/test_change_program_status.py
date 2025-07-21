from typing import Any, List

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.program.models import Program, ProgramCycle
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.program import ProgramFactory


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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)

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
            ("draft_to_active_without_permission", [Permissions.PROGRAMME_FINISH], Program.DRAFT, Program.ACTIVE),
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
    def test_status_change(
        self, _: Any, permissions: List[Permissions], initial_status: str, target_status: str
    ) -> None:
        data_collecting_type, _ = DataCollectingType.objects.update_or_create(
            **{"label": "Full", "code": "full_collection", "description": "Full"}
        )
        data_collecting_type.limit_to.add(self.business_area)
        program = ProgramFactory.create(
            status=initial_status,
            business_area=self.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.SELECTED_PARTNERS_ACCESS,
        )
        ProgramCycle.objects.filter(program=program).update(status=ProgramCycle.FINISHED)

        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(program.id, "ProgramNode"),
                    "status": target_status,
                }
            },
        )
