from django.core.cache import cache
from django.test import TestCase
import pytest

from extras.test_utils.factories import BusinessAreaFactory, HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.api.caches import (
    get_household_list_program_key,
    get_individual_list_program_key,
)
from hope.models import Household, Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def programs(business_area):
    return {
        "program1": ProgramFactory(business_area=business_area),
        "program2": ProgramFactory(business_area=business_area),
    }


def test_household_save_increments_cache(program):
    cache.clear()

    initial_version = get_household_list_program_key(program.id)
    HouseholdFactory(program=program, business_area=program.business_area)

    new_version = get_household_list_program_key(program.id)
    assert new_version > initial_version


def test_household_delete_increments_cache(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    cache.clear()

    initial_version = get_household_list_program_key(program.id)

    household.delete()

    new_version = get_household_list_program_key(program.id)
    assert new_version > initial_version


def test_household_bulk_update_increments_cache(program):
    households = [HouseholdFactory(program=program, business_area=program.business_area, size=1) for _ in range(3)]
    cache.clear()

    initial_version = get_household_list_program_key(program.id)

    for household in households:
        household.size = 5

    with TestCase.captureOnCommitCallbacks(execute=True):
        Household.objects.bulk_update(households, ["size"])

    new_version = get_household_list_program_key(program.id)
    assert new_version > initial_version


def test_individual_save_increments_both_caches(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    cache.clear()

    initial_household_version = get_household_list_program_key(program.id)
    initial_individual_version = get_individual_list_program_key(program.id)

    IndividualFactory(household=household, program=program, business_area=program.business_area)

    new_household_version = get_household_list_program_key(program.id)
    new_individual_version = get_individual_list_program_key(program.id)

    assert new_household_version > initial_household_version
    assert new_individual_version > initial_individual_version


def test_individual_delete_increments_both_caches(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    individual = IndividualFactory(household=household, program=program, business_area=program.business_area)
    cache.clear()

    initial_household_version = get_household_list_program_key(program.id)
    initial_individual_version = get_individual_list_program_key(program.id)

    individual.delete()

    new_household_version = get_household_list_program_key(program.id)
    new_individual_version = get_individual_list_program_key(program.id)

    assert new_household_version > initial_household_version
    assert new_individual_version > initial_individual_version


def test_individual_bulk_update_increments_both_caches(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    individuals = [
        IndividualFactory(household=household, program=program, business_area=program.business_area, full_name="Test")
        for _ in range(3)
    ]
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


def test_household_changes_only_affect_own_program_cache(programs):
    program1 = programs["program1"]
    program2 = programs["program2"]
    cache.clear()

    initial_version_p1 = get_household_list_program_key(program1.id)
    initial_version_p2 = get_household_list_program_key(program2.id)

    HouseholdFactory(program=program1, business_area=program1.business_area)

    new_version_p1 = get_household_list_program_key(program1.id)
    new_version_p2 = get_household_list_program_key(program2.id)

    assert new_version_p1 > initial_version_p1
    assert new_version_p2 == initial_version_p2


def test_individual_changes_only_affect_own_program_cache(programs):
    program1 = programs["program1"]
    program2 = programs["program2"]
    household1 = HouseholdFactory(program=program1, business_area=program1.business_area)
    cache.clear()

    initial_version_p1 = get_individual_list_program_key(program1.id)
    initial_version_p2 = get_individual_list_program_key(program2.id)

    IndividualFactory(household=household1, program=program1, business_area=program1.business_area)

    new_version_p1 = get_individual_list_program_key(program1.id)
    new_version_p2 = get_individual_list_program_key(program2.id)

    assert new_version_p1 > initial_version_p1
    assert new_version_p2 == initial_version_p2
