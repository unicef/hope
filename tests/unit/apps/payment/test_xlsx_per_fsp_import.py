from decimal import Decimal
from unittest.mock import MagicMock

from hope.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)


def _build_service(payments_dict: dict) -> XlsxPaymentPlanImportPerFspService:
    svc = XlsxPaymentPlanImportPerFspService.__new__(XlsxPaymentPlanImportPerFspService)
    svc.errors = []
    svc.sheetname = "TestSheet"
    svc.xlsx_headers = ["payment_id", "delivered_quantity"]
    svc.payments_dict = payments_dict
    return svc


def test_validate_delivered_quantity_uses_zero_when_entitlement_is_none() -> None:
    payment = MagicMock()
    payment.entitlement_quantity = None
    payment.delivered_quantity = None

    svc = _build_service({"PAY-001": payment})

    cell_payment_id = MagicMock()
    cell_payment_id.value = "PAY-001"

    cell_delivered = MagicMock()
    cell_delivered.value = Decimal(10)
    cell_delivered.coordinate = "B2"

    row = [cell_payment_id, cell_delivered]

    svc._validate_delivered_quantity(row)

    assert len(svc.errors) == 1
    error = svc.errors[0]
    assert error.sheet == "TestSheet"
    assert error.coordinates == "B2"
    assert "Delivered quantity 10" in error.message
    assert "Entitlement quantity 0" in error.message


def test_validate_delivered_quantity_no_error_when_within_entitlement() -> None:
    payment = MagicMock()
    payment.entitlement_quantity = None
    payment.delivered_quantity = None

    svc = _build_service({"PAY-002": payment})

    cell_payment_id = MagicMock()
    cell_payment_id.value = "PAY-002"

    cell_delivered = MagicMock()
    cell_delivered.value = Decimal(0)
    cell_delivered.coordinate = "B3"

    row = [cell_payment_id, cell_delivered]

    svc._validate_delivered_quantity(row)

    assert len(svc.errors) == 0
