from unittest.mock import patch

import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory
from hope.models import Household, Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def individual():
    return IndividualFactory()


@pytest.fixture
def household():
    return HouseholdFactory()


def test_individual_withdraw_sends_signal_by_default(individual: Individual) -> None:
    with patch("hope.models.individual.individual_withdrawn") as mock_signal:
        individual.withdraw()

    assert individual.withdrawn is True
    mock_signal.send.assert_called_once_with(sender=Individual, instance=individual)


def test_individual_withdraw_notify_false_does_not_send_signal(individual: Individual) -> None:
    with patch("hope.models.individual.individual_withdrawn") as mock_signal:
        individual.withdraw(notify=False)

    assert individual.withdrawn is True
    mock_signal.send.assert_not_called()


def test_household_withdraw_sends_signal_by_default(household: Household) -> None:
    with patch("hope.models.household.household_withdrawn") as mock_signal:
        household.withdraw()

    assert household.withdrawn is True
    mock_signal.send.assert_called_once_with(sender=Household, instance=household)


def test_household_withdraw_notify_false_does_not_send_signal(household: Household) -> None:
    with patch("hope.models.household.household_withdrawn") as mock_signal:
        household.withdraw(notify=False)

    assert household.withdrawn is True
    mock_signal.send.assert_not_called()
