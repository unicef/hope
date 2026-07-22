from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory
from hope.apps.household.services.locking import lock_household_then_individual
from hope.models import Household, Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def individual_with_household() -> Individual:
    individual = IndividualFactory(household=None)
    HouseholdFactory(
        business_area=individual.business_area,
        program=individual.program,
        registration_data_import=individual.registration_data_import,
        head_of_household=individual,
        create_role=False,
    )
    individual.refresh_from_db()
    return individual


@pytest.fixture
def individual_without_household() -> Individual:
    return IndividualFactory(household=None)


def test_lock_household_then_individual_locks_household_before_individual(
    individual_with_household: Individual,
) -> None:
    with CaptureQueriesContext(connection) as ctx:
        household, locked_individual = lock_household_then_individual(individual_with_household)

    assert household == individual_with_household.household
    assert locked_individual == individual_with_household

    for_update_queries = [q["sql"] for q in ctx.captured_queries if "FOR UPDATE" in q["sql"]]
    assert len(for_update_queries) == 2
    assert Household._meta.db_table in for_update_queries[0]
    assert Individual._meta.db_table in for_update_queries[1]


def test_lock_household_then_individual_without_household(
    individual_without_household: Individual,
) -> None:
    household, locked_individual = lock_household_then_individual(individual_without_household)

    assert household is None
    assert locked_individual == individual_without_household
