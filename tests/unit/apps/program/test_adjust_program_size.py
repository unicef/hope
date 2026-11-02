from io import StringIO

from django.core.management import call_command
import pytest

from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.household.const import NON_BENEFICIARY
from hope.apps.program.api.filters import ProgramFilter
from hope.models import Program

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


def test_recount_program_size_command_fixes_stale_counters(program):
    head = IndividualFactory(household=None, program=program, business_area=program.business_area)
    HouseholdFactory(
        program=program,
        business_area=program.business_area,
        head_of_household=head,
        registration_data_import=head.registration_data_import,
    )
    withdrawn_head = IndividualFactory(
        household=None,
        program=program,
        business_area=program.business_area,
        withdrawn=True,
    )
    HouseholdFactory(
        program=program,
        business_area=program.business_area,
        withdrawn=True,
        head_of_household=withdrawn_head,
        registration_data_import=withdrawn_head.registration_data_import,
    )
    Program.objects.filter(pk=program.pk).update(household_count=999, individual_count=999)

    call_command("recount_program_size")

    program.refresh_from_db()
    assert program.household_count == 1
    assert program.individual_count == 1


def test_filter_number_of_households_excludes_withdrawn(program):
    HouseholdFactory(program=program, business_area=program.business_area)
    HouseholdFactory(program=program, business_area=program.business_area, withdrawn=True)

    filtered = ProgramFilter(data={"number_of_households_min": 2}, queryset=Program.objects.filter(pk=program.pk)).qs

    assert list(filtered) == []


def test_recount_program_size_command_recounts_program_that_fails_validation(program):
    program.payment_plan_purposes.clear()
    HouseholdFactory(program=program, business_area=program.business_area)
    Program.objects.filter(pk=program.pk).update(household_count=999, individual_count=999)

    call_command("recount_program_size")

    program.refresh_from_db()
    assert program.household_count == 1
    assert program.individual_count == 1


def test_recount_program_size_command_writes_nothing_when_counts_are_current(program):
    HouseholdFactory(program=program, business_area=program.business_area)
    call_command("recount_program_size")
    output = StringIO()

    call_command("recount_program_size", stdout=output)

    assert "updated 0" in output.getvalue()
