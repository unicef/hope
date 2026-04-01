"""Tests for create_needs_adjudication_tickets_for_biometrics guard branches."""

from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    close_needs_adjudication_new_ticket,
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


@patch(
    "hope.apps.grievance.services.needs_adjudication_ticket_services.validate_all_individuals_before_close_needs_adjudication"
)
@patch("hope.apps.grievance.services.needs_adjudication_ticket_services.mark_as_distinct_individual")
@patch("hope.apps.grievance.services.needs_adjudication_ticket_services._clear_deduplication_individuals_fields")
@patch("hope.apps.grievance.services.needs_adjudication_ticket_services.logger")
@patch(
    "hope.apps.registration_data.services.biometric_deduplication.BiometricDeduplicationService.__init__",
    return_value=None,
)
def test_close_needs_adjudication_logs_error_when_program_is_none(
    mock_bds_init: MagicMock,
    mock_logger: MagicMock,
    mock_clear: MagicMock,
    mock_mark_distinct: MagicMock,
    mock_validate: MagicMock,
) -> None:
    individual_a = MagicMock()
    individual_a.photo.name = "photo_a.jpg"
    individual_b = MagicMock()
    individual_b.photo.name = "photo_b.jpg"

    ticket = MagicMock()
    ticket.issue_type = GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY
    ticket.programs.all.return_value = []
    ticket.registration_data_import.program = None

    ticket_details = MagicMock()
    ticket_details.ticket = ticket
    ticket_details.selected_individuals.all.return_value = []
    ticket_details.selected_distinct.all.return_value = [individual_a, individual_b]

    user = MagicMock()

    close_needs_adjudication_new_ticket(ticket_details, user)

    mock_logger.error.assert_called_once_with("Cannot report false positive duplicate: program is None")
