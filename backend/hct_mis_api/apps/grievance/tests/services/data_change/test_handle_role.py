from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.services.data_change.utils import handle_role
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_NO_ROLE,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class Test(TestCase):
    def test_handle_role(self) -> None:
        business_area = create_afghanistan()
        program = ProgramFactory(
            name="Test Program",
            business_area=business_area,
            status=Program.ACTIVE,
        )
        household = HouseholdFactory.build()
        household.registration_data_import.save()
        household.household_collection.save()
        household.registration_data_import.imported_by.save()
        household.programs.add(program)
        individual = IndividualFactory(household=household, program=program)
        household.head_of_household = individual
        household.save()
        IndividualRoleInHousehold.objects.create(household=household, individual=individual, role=ROLE_ALTERNATE)

        self.assertEqual(
            IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count(), 1
        )

        handle_role(ROLE_NO_ROLE, household, individual)

        self.assertEqual(
            IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count(), 0
        )
