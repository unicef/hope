import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory, IndividualRoleInHouseholdFactory

pytestmark = pytest.mark.django_db


def test_household_factories():
    assert IndividualFactory()
    assert HouseholdFactory()
    assert IndividualRoleInHouseholdFactory()
