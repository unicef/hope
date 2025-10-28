import pytest
from rest_framework.exceptions import ValidationError
from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.grievance.services.data_change.utils import handle_role
from hope.apps.household.models import (
    ROLE_ALTERNATE,
    IndividualRoleInHousehold, ROLE_PRIMARY,
)
from hope.apps.program.models import Program
from hope.apps.utils.models import MergeStatusModel


class TestHandleRole(TestCase):
    def test_handle_role_alternate_into_primary(self) -> None:
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
        assert IndividualRoleInHousehold.objects.get(household=household, individual=individual).role == ROLE_ALTERNATE

        handle_role(household, individual, ROLE_PRIMARY)

        assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1
        assert IndividualRoleInHousehold.objects.get(household=household, individual=individual).role == ROLE_PRIMARY

    def test_handle_role_no_role_into_alternate(self) -> None:
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

        assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 0

        # Add a role
        handle_role(household, individual, ROLE_ALTERNATE)

        assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1
        assert IndividualRoleInHousehold.objects.get(household=household, individual=individual).role == ROLE_ALTERNATE

    def test_handle_role_alternate_into_no_role(self) -> None:
        """Test that handle_role updates an existing role"""
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

        # Update to None (should remove the role)
        handle_role(household, individual, None)

        assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 0

    def test_handle_role_primary_into_no_role(self) -> None:
        """Test that handle_role raises ValidationError when trying to remove PRIMARY role"""
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
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1

        # Attempting to remove PRIMARY role should raise ValidationError
        with pytest.raises(ValidationError, match="Ticket cannot be closed, primary collector role has to be reassigned"):
            handle_role(household, individual, None)
