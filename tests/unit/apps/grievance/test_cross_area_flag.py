"""Tests for cross-area flag on grievance tickets."""

from typing import Any

import pytest

from extras.test_utils.factories import BusinessAreaFactory, HouseholdFactory, IndividualFactory
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.grievance import TicketNeedsAdjudicationDetailsFactory
from hope.models import Area, BusinessArea, Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_area1() -> Area:
    return AreaFactory()


@pytest.fixture
def admin_area2() -> Area:
    return AreaFactory()


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def individual1_from_area1(business_area: BusinessArea, admin_area1: Area) -> Individual:
    individual = IndividualFactory(business_area=business_area, household=None)
    household = HouseholdFactory(
        business_area=business_area,
        admin2=admin_area1,
        head_of_household=individual,
    )
    individual.household = household
    individual.save()
    return individual


@pytest.fixture
def individual2_from_area1(business_area: BusinessArea, admin_area1: Area) -> Individual:
    individual = IndividualFactory(business_area=business_area, household=None)
    household = HouseholdFactory(
        business_area=business_area,
        admin2=admin_area1,
        head_of_household=individual,
    )
    individual.household = household
    individual.save()
    return individual


@pytest.fixture
def individual_from_area2(business_area: BusinessArea, admin_area2: Area) -> Individual:
    individual = IndividualFactory(business_area=business_area, household=None)
    household = HouseholdFactory(
        business_area=business_area,
        admin2=admin_area2,
        head_of_household=individual,
    )
    individual.household = household
    individual.save()
    return individual


@pytest.fixture
def individual_without_household(business_area: BusinessArea) -> Individual:
    return IndividualFactory(business_area=business_area, household=None)


@pytest.fixture
def needs_adjudication_ticket_cross_area(individual1_from_area1: Individual, individual_from_area2: Individual) -> Any:
    ticket = TicketNeedsAdjudicationDetailsFactory(
        golden_records_individual=individual1_from_area1,
    )
    ticket.possible_duplicates.set([individual_from_area2])
    return ticket


@pytest.fixture
def needs_adjudication_ticket_same_area(individual1_from_area1: Individual, individual2_from_area1: Individual) -> Any:
    ticket = TicketNeedsAdjudicationDetailsFactory(
        golden_records_individual=individual1_from_area1,
    )
    ticket.possible_duplicates.set([individual2_from_area1])
    return ticket


@pytest.fixture
def needs_adjudication_ticket_ind_no_household(
    individual_without_household: Individual, individual_from_area2: Individual
) -> Any:
    ticket = TicketNeedsAdjudicationDetailsFactory(
        golden_records_individual=individual_without_household,
    )
    ticket.possible_duplicates.set([individual_from_area2])
    return ticket


def test_cross_area_flag_is_true_for_cross_area_ticket(needs_adjudication_ticket_cross_area: Any) -> None:
    needs_adjudication_ticket_cross_area.populate_cross_area_flag()
    needs_adjudication_ticket_cross_area.refresh_from_db()
    assert needs_adjudication_ticket_cross_area.is_cross_area is True


def test_cross_area_flag_is_false_for_same_area_ticket(needs_adjudication_ticket_same_area: Any) -> None:
    needs_adjudication_ticket_same_area.populate_cross_area_flag()
    needs_adjudication_ticket_same_area.refresh_from_db()
    assert needs_adjudication_ticket_same_area.is_cross_area is False


def test_cross_area_flag_is_false_for_individual_without_household(
    needs_adjudication_ticket_ind_no_household: Any,
) -> None:
    needs_adjudication_ticket_ind_no_household.populate_cross_area_flag()
    needs_adjudication_ticket_ind_no_household.refresh_from_db()
    assert needs_adjudication_ticket_ind_no_household.is_cross_area is False
