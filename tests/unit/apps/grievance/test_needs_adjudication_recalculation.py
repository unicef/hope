"""Marking an individual duplicate or distinct must refresh the household composition counters."""

import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    mark_as_distinct_individual,
    mark_as_duplicate_individual,
)
from hope.apps.household.services.household_recalculate_data import recalculate_data

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def program():
    return ProgramFactory(data_collecting_type=DataCollectingTypeFactory(recalculate_composition=True))


@pytest.fixture
def household(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        registration_data_import=household.registration_data_import,
    )
    recalculate_data(household)
    household.refresh_from_db()
    return household


@pytest.fixture
def household_with_duplicate_member(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        duplicate=True,
        registration_data_import=household.registration_data_import,
    )
    recalculate_data(household)
    household.refresh_from_db()
    return household


def test_mark_as_duplicate_individual_recalculates_household_size(household, program):
    assert household.size == 2
    member = household.individuals.exclude(pk=household.head_of_household_id).get()

    mark_as_duplicate_individual(member, None, household, UserFactory(), program)

    household.refresh_from_db()
    assert household.size == 1


def test_mark_as_distinct_individual_recalculates_household_size(household_with_duplicate_member, program):
    household = household_with_duplicate_member
    assert household.size == 1
    member = household.individuals.exclude(pk=household.head_of_household_id).get()

    mark_as_distinct_individual(member, UserFactory(), program)

    household.refresh_from_db()
    assert household.size == 2
