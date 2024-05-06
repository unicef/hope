from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestHouseholdRegistrationId(APITestCase):
    QUERY = """
    query Household($id: ID!) {
      household(id: $id) {
        registrationId
      }
    }
    """

    partner: Partner
    user: User
    business_area: BusinessArea
    program: Program
    household: Household

    @classmethod
    def setUpTestData(cls) -> None:
        generate_data_collecting_types()

        cls.business_area = create_afghanistan()
        cls.partner = PartnerFactory(name="UNICEF")
        cls.user = UserFactory.create(partner=cls.partner)
        cls.program = ProgramFactory(
            name="Test program",
            business_area=cls.business_area,
            status=Program.ACTIVE,
            data_collecting_type=DataCollectingType.objects.get(code="partial_individuals"),
        )

        cls.household, _ = create_household(
            {
                "size": 2,
                "program": cls.program,
            },
        )
        super().setUpTestData()

    @parameterized.expand(
        [
            ("ABCD-123123#0",),
            ("ABCD-123123#1",),
            (None,),
            ("",),
        ]
    )
    def test_household_registration_id(self, registration_id: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS], self.business_area
        )

        self.household.registration_id = registration_id
        self.household.save(update_fields=["registration_id"])

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )
