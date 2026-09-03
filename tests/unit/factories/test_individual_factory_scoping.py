"""IndividualFactory must not invent a business area for a household member."""

import pytest

from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory


@pytest.fixture
def household():
    return HouseholdFactory()


@pytest.fixture
def other_household():
    return HouseholdFactory()


def test_member_inherits_the_household_business_area(db, household):
    member = IndividualFactory(household=household)

    assert member.business_area_id == household.business_area_id


def test_member_inherits_the_household_program(db, household):
    member = IndividualFactory(household=household)

    assert member.program_id == household.program_id


def test_individual_without_a_household_gets_its_own_business_area(db):
    first = IndividualFactory()
    second = IndividualFactory()

    assert first.household is None
    assert first.business_area_id != second.business_area_id


def test_individual_without_a_household_stays_consistent_with_its_program(db):
    individual = IndividualFactory()

    assert individual.program.business_area_id == individual.business_area_id


def test_explicit_business_area_overrides_the_household(db, household, other_household):
    member = IndividualFactory(household=household, business_area=other_household.business_area)

    assert member.business_area_id == other_household.business_area_id
