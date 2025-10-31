from django.core.cache import cache
import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.household.api.caches import (
    get_household_list_program_key,
    get_individual_list_program_key,
)
from hope.models.household import Household
from hope.models.individual import Individual

pytestmark = pytest.mark.django_db(transaction=True)


class TestHouseholdCacheSignals:
    def test_household_save_increments_cache(self):
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        cache.clear()

        initial_version = get_household_list_program_key(program.id)
        HouseholdFactory(program=program)

        new_version = get_household_list_program_key(program.id)
        assert new_version > initial_version

    def test_household_delete_increments_cache(self):
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        household = HouseholdFactory(program=program)
        cache.clear()

        initial_version = get_household_list_program_key(program.id)

        household.delete()

        new_version = get_household_list_program_key(program.id)
        assert new_version > initial_version

    def test_household_bulk_update_increments_cache(self):
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        households = [HouseholdFactory(program=program, size=1) for _ in range(3)]
        cache.clear()

        initial_version = get_household_list_program_key(program.id)

        for household in households:
            household.size = 5

        Household.objects.bulk_update(households, ["size"])

        new_version = get_household_list_program_key(program.id)
        assert new_version > initial_version


class TestIndividualCacheSignals:
    def test_individual_save_increments_both_caches(self):
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        household = HouseholdFactory(program=program)
        cache.clear()

        initial_household_version = get_household_list_program_key(program.id)
        initial_individual_version = get_individual_list_program_key(program.id)

        IndividualFactory(household=household, program=program)

        new_household_version = get_household_list_program_key(program.id)
        new_individual_version = get_individual_list_program_key(program.id)

        assert new_household_version > initial_household_version
        assert new_individual_version > initial_individual_version

    def test_individual_delete_increments_both_caches(self):
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        household = HouseholdFactory(program=program)
        individual = IndividualFactory(household=household, program=program)
        cache.clear()

        initial_household_version = get_household_list_program_key(program.id)
        initial_individual_version = get_individual_list_program_key(program.id)

        individual.delete()

        new_household_version = get_household_list_program_key(program.id)
        new_individual_version = get_individual_list_program_key(program.id)

        assert new_household_version > initial_household_version
        assert new_individual_version > initial_individual_version

    def test_individual_bulk_update_increments_both_caches(self):
        """Test that bulk_update increments both household and individual list caches."""
        from django.test import TestCase

        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area)
        household = HouseholdFactory(program=program)
        individuals = [IndividualFactory(household=household, program=program, full_name="Test") for _ in range(3)]
        cache.clear()

        initial_household_version = get_household_list_program_key(program.id)
        initial_individual_version = get_individual_list_program_key(program.id)

        for individual in individuals:
            individual.full_name = "Updated"

        with TestCase.captureOnCommitCallbacks(execute=True):
            Individual.objects.bulk_update(individuals, ["full_name"])

        new_household_version = get_household_list_program_key(program.id)
        new_individual_version = get_individual_list_program_key(program.id)

        assert new_household_version > initial_household_version
        assert new_individual_version > initial_individual_version


class TestMultipleProgramsCacheIsolation:
    def test_household_changes_only_affect_own_program_cache(self):
        business_area = create_afghanistan()
        program1 = ProgramFactory(business_area=business_area)
        program2 = ProgramFactory(business_area=business_area)
        cache.clear()

        initial_version_p1 = get_household_list_program_key(program1.id)
        initial_version_p2 = get_household_list_program_key(program2.id)

        HouseholdFactory(program=program1)

        new_version_p1 = get_household_list_program_key(program1.id)
        new_version_p2 = get_household_list_program_key(program2.id)

        assert new_version_p1 > initial_version_p1
        assert new_version_p2 == initial_version_p2

    def test_individual_changes_only_affect_own_program_cache(self):
        business_area = create_afghanistan()
        program1 = ProgramFactory(business_area=business_area)
        program2 = ProgramFactory(business_area=business_area)
        household1 = HouseholdFactory(program=program1)
        cache.clear()

        initial_version_p1 = get_individual_list_program_key(program1.id)
        initial_version_p2 = get_individual_list_program_key(program2.id)

        IndividualFactory(household=household1, program=program1)

        new_version_p1 = get_individual_list_program_key(program1.id)
        new_version_p2 = get_individual_list_program_key(program2.id)

        assert new_version_p1 > initial_version_p1
        assert new_version_p2 == initial_version_p2
