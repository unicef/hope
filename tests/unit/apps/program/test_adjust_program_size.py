import pytest

from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.household.const import NON_BENEFICIARY

pytestmark = pytest.mark.django_db


@pytest.fixture
def program():
    return ProgramFactory()


def test_adjust_program_size_counts_active_households_and_individuals(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        registration_data_import=household.registration_data_import,
    )

    program.adjust_program_size()

    assert program.household_count == 1
    assert program.individual_count == 2


def test_adjust_program_size_excludes_withdrawn_households(program):
    HouseholdFactory(program=program, business_area=program.business_area)
    HouseholdFactory(program=program, business_area=program.business_area, withdrawn=True)

    program.adjust_program_size()

    assert program.household_count == 1


def test_adjust_program_size_excludes_withdrawn_individuals(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        withdrawn=True,
        registration_data_import=household.registration_data_import,
    )

    program.adjust_program_size()

    assert program.individual_count == 1


def test_adjust_program_size_excludes_duplicate_individuals(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        duplicate=True,
        registration_data_import=household.registration_data_import,
    )

    program.adjust_program_size()

    assert program.individual_count == 1


def test_adjust_program_size_excludes_non_beneficiary_individuals(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        relationship=NON_BENEFICIARY,
        registration_data_import=household.registration_data_import,
    )

    program.adjust_program_size()

    assert program.individual_count == 1
