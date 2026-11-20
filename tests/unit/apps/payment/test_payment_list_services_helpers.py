from unittest.mock import MagicMock

import pytest

from hope.apps.payment.services.payment_list_services import PaymentListService


@pytest.fixture
def payment_list_service():
    service = object.__new__(PaymentListService)
    service.payment_list = MagicMock()
    return service


def test_build_payments_chunks_unknown_split_type(payment_list_service):
    """When split_type is unrecognized, _build_payments_chunks returns an empty list."""
    result = payment_list_service._build_payments_chunks(
        split_type="UNKNOWN_TYPE",
        chunks_no=None,
        payments=MagicMock(),
        payments_count=10,
    )

    assert result == []
