from django.test import TestCase

from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.grievance.services.data_change.utils import handle_role
from tests.extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_NO_ROLE,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.models import MergeStatusModel


class TestHandleRole(TestCase):
    def test_handle_role(self) -> None:
        business_area = create_afghanistan()
        program = ProgramFactory(
            name="Test Program",
            business_area=business_area,
            status=Program.ACTIVE,
        )
        household = HouseholdFactory.build(program=program)
        household.household_collection.save()
        household.registration_data_import.imported_by.save()
        household.registration_data_import.program = household.program
        household.registration_data_import.save()
        individual = IndividualFactory(household=household, program=program)
        household.head_of_household = individual
        household.save()
        IndividualRoleInHousehold.objects.create(
            household=household,
            individual=individual,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        self.assertEqual(
            IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count(), 1
        )

        handle_role(ROLE_NO_ROLE, household, individual)

        self.assertEqual(
            IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count(), 0
        )
