from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.one_time_scripts.update_program_size import update_program_size


class TestUpdateProgramSize(TestCase):
    def test_update_program_size(self) -> None:
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        households_ids = []
        individuals_ids = []
        for _ in range(3):
            hh, inds = create_household({"size": 3})
            households_ids.append(hh.id)
            individuals_ids.extend([ind.id for ind in inds])

        Household.objects.filter(id__in=households_ids).update(program_id=program.id)
        Individual.objects.filter(id__in=individuals_ids).update(program_id=program.id)

        assert program.household_count == 0
        assert program.individual_count == 0

        update_program_size()

        program.refresh_from_db()

        assert program.household_count == 3
        assert program.individual_count == 9
