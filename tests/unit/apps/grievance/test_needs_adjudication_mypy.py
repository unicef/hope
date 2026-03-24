"""Tests for create_needs_adjudication_tickets_for_biometrics guard branches."""

from decimal import Decimal
from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DeduplicationEngineSimilarityPairFactory,
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
def business_area() -> Any:
    return BusinessAreaFactory(slug="na-mypy-ba")


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area, biometric_deduplication_enabled=True)


@pytest.fixture
def rdi(program: Any, business_area: Any) -> Any:
    return RegistrationDataImportFactory(program=program, business_area=business_area)


@pytest.fixture
def pair_both_individuals_none(program: Any) -> Any:
    """A similarity pair where both individual1 and individual2 are None."""
    return DeduplicationEngineSimilarityPair.objects.create(
        program=program,
        individual1=None,
        individual2=None,
        similarity_score=Decimal("0.00"),
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_500,
    )


def test_create_needs_adjudication_tickets_for_biometrics_raises_when_both_individuals_none(
    pair_both_individuals_none: Any,
    rdi: Any,
) -> None:
    """When both individual1 and individual2 are None, a ValueError is raised."""
    pairs_qs = DeduplicationEngineSimilarityPair.objects.filter(id=pair_both_individuals_none.id)

    with pytest.raises(ValueError, match="pair.individual2 must not be None"):
        create_needs_adjudication_tickets_for_biometrics(pairs_qs, rdi)
