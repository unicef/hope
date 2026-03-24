from unittest.mock import MagicMock

import pytest

from hope.apps.payment.services.payment_plan_services import PaymentPlanService


@pytest.fixture
def payment_plan_service():
    service = object.__new__(PaymentPlanService)
    service.payment_plan = MagicMock()
    return service


def test_build_payments_chunks_unknown_split_type(payment_plan_service):
    """When split_type is unrecognized, _build_payments_chunks returns an empty list."""
    result = payment_plan_service._build_payments_chunks(
        split_type="UNKNOWN_TYPE",
        chunks_no=None,
        payments=MagicMock(),
        payments_count=10,
    )

    assert result == []
