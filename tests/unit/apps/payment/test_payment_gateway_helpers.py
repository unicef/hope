from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from hope.apps.payment.services.payment_gateway import (
    FlexibleArgumentsDataclassMixin,
    PaymentGatewayService,
    PaymentRecordData,
)


@pytest.fixture
def gateway_service():
    service = object.__new__(PaymentGatewayService)
    service.api = MagicMock()
    service.ADD_RECORDS_CHUNK_SIZE = 500
    service.change_payment_instruction_status = MagicMock()
    return service


@pytest.fixture
def mock_container():
    return MagicMock()


@patch("hope.apps.payment.services.payment_gateway.chunks", return_value=iter([]))
def test_add_records_empty_payments_no_container_update(mock_chunks, gateway_service, mock_container):
    """When payments is empty (falsy), container.save and change_payment_instruction_status are NOT called."""
    gateway_service._add_records_to_container([], mock_container)

    mock_container.save.assert_not_called()
    gateway_service.change_payment_instruction_status.assert_not_called()


@patch("hope.apps.payment.services.payment_gateway.chunks")
def test_add_records_success_updates_container(mock_chunks, gateway_service, mock_container):
    """When response has no errors, container is updated and status changes are triggered."""
    gateway_service._handle_pg_success = MagicMock()
    gateway_service._handle_pg_errors = MagicMock()

    chunk = [MagicMock(), MagicMock()]
    mock_chunks.return_value = iter([chunk])

    response = MagicMock()
    response.errors = None
    gateway_service.api.add_records_to_payment_instruction.return_value = response

    payments = MagicMock()
    payments.__bool__ = MagicMock(return_value=True)

    gateway_service._add_records_to_container(payments, mock_container)

    gateway_service._handle_pg_success.assert_called_once_with(response, chunk)
    gateway_service._handle_pg_errors.assert_not_called()
    assert mock_container.sent_to_payment_gateway is True
    mock_container.save.assert_called_once_with(update_fields=["sent_to_payment_gateway"])
    assert gateway_service.change_payment_instruction_status.call_count == 2


def test_create_from_dict_raises_on_non_dataclass():
    class NotADataclass(FlexibleArgumentsDataclassMixin):
        pass

    with pytest.raises(TypeError, match="must be called with a dataclass type or instance"):
        NotADataclass.create_from_dict({"key": "value"})


def test_get_hope_status_callable_path():
    """Exercise the callable branch of hope_status() if callable(hope_status) else hope_status."""
    record = PaymentRecordData(
        id=1,
        remote_id="123",
        created="2024-01-01",
        modified="2024-01-01",
        record_code="REC-1",
        parent="PARENT-1",
        status="TRANSFERRED_TO_BENEFICIARY",
        auth_code="AUTH",
        fsp_code="FSP",
        payout_amount=10.0,
    )
    result = record.get_hope_status(Decimal("10.00"))
    assert isinstance(result, str)
