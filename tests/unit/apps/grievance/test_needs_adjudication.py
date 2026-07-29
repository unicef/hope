"""Tests for create_needs_adjudication_tickets_for_biometrics guard branches."""

from decimal import Decimal

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets_for_biometrics,
)
from hope.models import DeduplicationEngineSimilarityPair

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> object:
    return BusinessAreaFactory(slug="na-mypy-ba")


@pytest.fixture
def program(business_area: object) -> object:
    return ProgramFactory(business_area=business_area, biometric_deduplication_enabled=True)


@pytest.fixture
def rdi(program: object, business_area: object) -> object:
    return RegistrationDataImportFactory(program=program, business_area=business_area)


@pytest.fixture
def pair_both_individuals_none(program: object) -> object:
    """A similarity pair where both individual1 and individual2 are None."""
    return DeduplicationEngineSimilarityPair.objects.create(
        program=program,
        individual1=None,
        individual2=None,
        similarity_score=Decimal("0.00"),
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_500,
    )


def test_create_needs_adjudication_tickets_for_biometrics_skips_pair_when_both_individuals_none(
    pair_both_individuals_none: object,
    rdi: object,
) -> None:
    """When both individual1 and individual2 are None, the pair is skipped."""
    from hope.apps.grievance.models import GrievanceTicket

    pairs_qs = DeduplicationEngineSimilarityPair.objects.filter(id=pair_both_individuals_none.id)

    create_needs_adjudication_tickets_for_biometrics(pairs_qs, rdi)

    assert not GrievanceTicket.objects.exists()
