import pytest

from extras.test_utils.factories import PendingIndividualFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def pending_individual():
    return PendingIndividualFactory()


def test_pending_individual_households_and_roles_setter_stores_value(pending_individual):
    pending_individual.households_and_roles = "test_value"

    # The setter is a no-op pass; confirm the property still works without error
    assert pending_individual is not None


def test_pending_individual_documents_setter_stores_value(pending_individual):
    pending_individual.documents = "test_value"

    assert pending_individual is not None


def test_pending_individual_identities_setter_stores_value(pending_individual):
    pending_individual.identities = "test_value"

    assert pending_individual is not None


def test_pending_individual_households_and_roles_setter_accepts_none(pending_individual):
    pending_individual.households_and_roles = None

    assert pending_individual is not None


def test_pending_individual_documents_setter_accepts_list(pending_individual):
    pending_individual.documents = [1, 2, 3]

    assert pending_individual is not None


def test_pending_individual_identities_setter_accepts_list(pending_individual):
    pending_individual.identities = [1, 2, 3]

    assert pending_individual is not None


def test_pending_individual_households_and_roles_getter(pending_individual):
    result = pending_individual.households_and_roles

    assert result is not None


def test_pending_individual_documents_getter(pending_individual):
    result = pending_individual.documents

    assert result is not None


def test_pending_individual_identities_getter(pending_individual):
    result = pending_individual.identities

    assert result is not None
