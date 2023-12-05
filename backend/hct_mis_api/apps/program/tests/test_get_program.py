from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

PROGRAM_QUERY = """
query Program($id: ID!) {
  program(id: $id) {
    name
    startDate
    endDate
    status
  }
}
"""


class TestGetProgram(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(
            name="test_program",
            start_date="2023-11-11",
            end_date="2023-11-21",
            status=Program.ACTIVE,
            business_area=cls.business_area,
        )

        cls.partner_1 = PartnerFactory(name="NOT_UNICEF")
        cls.partner_1.permissions = {str(cls.business_area.id): {"programs": {str(cls.program.id): ["some_uuid"]}}}
        cls.partner_1.save()
        cls.user_1 = UserFactory(partner=cls.partner_1)

        cls.partner_2 = PartnerFactory(name="NOT_UNICEF_2")
        cls.user_2 = UserFactory(partner=cls.partner_2)

    def test_user_access_program_with_his_partner(self) -> None:
        self.create_user_role_with_permissions(
            self.user_1, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=PROGRAM_QUERY,
            context={"user": self.user_1},
            variables={"id": self.id_to_base64(self.program.id, "ProgramNode")},
        )

    def test_user_does_not_access_program_with_another_partner(self) -> None:
        self.create_user_role_with_permissions(
            self.user_2, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=PROGRAM_QUERY,
            context={"user": self.user_2},
            variables={"id": self.id_to_base64(self.program.id, "ProgramNode")},
        )
