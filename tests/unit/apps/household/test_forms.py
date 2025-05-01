from django.test import TestCase

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.forms import MassEnrollForm
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class MassEnrollFormTest(TestCase):
    def setUp(self) -> None:
        afg = create_afghanistan()
        self.business_area_id = str(afg.id)
        partial = DataCollectingTypeFactory(
            business_areas=[afg],
        )
        partial.compatible_types.add(partial)
        self.program = ProgramFactory(
            name="Test Program 333", business_area_id=afg.id, status=Program.ACTIVE, data_collecting_type=partial
        )
        self.household = HouseholdFactory(
            program=self.program,
            head_of_household=IndividualFactory(household=None),
        )

    def test_clean_form(self) -> None:
        form_data = {"program_for_enroll": self.program.id, "apply": True}
        form = MassEnrollForm(
            data=form_data,
            business_area_id=self.business_area_id,
            households=Household.objects.filter(id=self.household.id),
        )
        assert form.is_valid()
