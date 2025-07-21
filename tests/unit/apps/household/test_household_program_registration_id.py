from parameterized import parameterized

from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.models import Program
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.core import (
    create_afghanistan,
    generate_data_collecting_types,
)
from tests.extras.test_utils.factories.household import (
    HouseholdFactory,
    create_household,
)
from tests.extras.test_utils.factories.program import ProgramFactory
from tests.extras.test_utils.factories.registration_data import (
    RegistrationDataImportFactory,
)


class TestHouseholdRegistrationId(APITestCase):
    QUERY = """
    query Household($id: ID!) {
      household(id: $id) {
        programRegistrationId
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
        super().setUpTestData()
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

    @parameterized.expand(
        [
            ("ABCD-123123",),
            (None,),
            ("",),
        ]
    )
    def test_household_program_registration_id(self, program_registration_id: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS], self.business_area
        )

        self.household.program_registration_id = program_registration_id
        self.household.save(update_fields=["program_registration_id"])
        self.household.refresh_from_db()
        expected_program_registration_id = f"{program_registration_id}#0" if program_registration_id else None
        self.assertEqual(self.household.program_registration_id, expected_program_registration_id)

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

    def test_program_program_registration_id_trigger(self) -> None:
        rdi = RegistrationDataImportFactory(business_area=self.business_area, program=self.program)
        HouseholdFactory(
            registration_data_import=rdi,
            program_registration_id="ABCD-123123",
        )
        HouseholdFactory(
            registration_data_import=rdi,
            program_registration_id="ABCD-123123",
        )
        HouseholdFactory(
            registration_data_import=rdi,
            program_registration_id="ABCD-123123",
        )
        HouseholdFactory(
            registration_data_import=rdi,
            program_registration_id="ABCD-111222",
        )
        registrations_ids = list(
            Household.objects.filter(registration_data_import=rdi)
            .order_by("program_registration_id")
            .values_list("program_registration_id", flat=True)
        )
        expected_program_registrations_ids = ["ABCD-111222#0", "ABCD-123123#0", "ABCD-123123#1", "ABCD-123123#2"]
        self.assertEqual(registrations_ids, expected_program_registrations_ids)
