from django.test import TestCase

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.forms import MassEnrollForm
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class MassEnrollFormTest(TestCase):
    def setUp(self) -> None:
        afg = create_afghanistan()
        self.business_area_id = str(afg.id)
        partial = DataCollectingTypeFactory(business_areas=[afg])
        self.program = ProgramFactory(
            name="Test Program 333", business_area_id=afg.id, status=Program.ACTIVE, data_collecting_type=partial
        )
        self.rdi = RegistrationDataImportFactory(name="Test RDI NEW 123", program=self.program, business_area_id=afg.id)

        self.household = HouseholdFactory(
            program=self.program,
            head_of_household=IndividualFactory(household=None),
        )

    def test_clean_rdi_not_belong_to_program(self) -> None:
        different_program = ProgramFactory(
            name="Diff Program",
        )
        different_rdi = RegistrationDataImportFactory(
            name="Diff RDI",
            program=different_program,
        )
        form_data = {"program_for_enroll": self.program.id, "rdi": different_rdi.id, "apply": True}
        form = MassEnrollForm(data=form_data, business_area_id=self.business_area_id, households=[self.household])
        self.assertFalse(form.is_valid())
        self.assertIn(f"RDI not belong to the program {self.program.name}", form.errors.get("__all__", []))
