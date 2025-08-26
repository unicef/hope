from django.test import TestCase
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.grievance.services.data_change.utils import handle_role
from hope.models.household import (
    ROLE_ALTERNATE,
    ROLE_NO_ROLE,
)
from hope.models.individual_role_in_household import IndividualRoleInHousehold
from hope.models.program import Program
from hope.models.utils import MergeStatusModel


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

        assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1

        handle_role(ROLE_NO_ROLE, household, individual)

        assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 0
