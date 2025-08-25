from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import (
    create_afghanistan,
    generate_data_collecting_types,
)
from extras.test_utils.factories.household import HouseholdFactory, create_household
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from models.account import Partner, User
from hope.apps.core.base_test_case import BaseTestCase
from models.core import BusinessArea, DataCollectingType
from models.household import Household
from models.program import Program


class TestHouseholdRegistrationIdTrigger(BaseTestCase):
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
        unicef_partner = PartnerFactory(name="UNICEF")
        cls.partner = PartnerFactory(name="UNICEF HQ", parent=unicef_partner)
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
        expected_program_registrations_ids = [
            "ABCD-111222#0",
            "ABCD-123123#0",
            "ABCD-123123#1",
            "ABCD-123123#2",
        ]
        assert registrations_ids == expected_program_registrations_ids
