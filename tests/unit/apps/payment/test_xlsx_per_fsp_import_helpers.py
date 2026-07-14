"""Tests for XlsxPaymentPlanDeliveryImportService extracted helpers."""

import datetime
from datetime import UTC
from decimal import Decimal
import io
from unittest.mock import MagicMock

import pytest
import pytz

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramFactory,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_import_service import (
    XlsxPaymentPlanDeliveryImportService,
)
from hope.models import (
    BusinessArea,
    Payment,
    PaymentPlan,
    PaymentVerification,
    Program,
    ProgramCycle,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program: Program) -> ProgramCycle:
    return program.cycles.first()


@pytest.fixture
def payment_plan(program_cycle: ProgramCycle, business_area: BusinessArea) -> PaymentPlan:
    pp = PaymentPlanFactory(
        program_cycle=program_cycle,
        business_area=business_area,
        create_payment_verification_summary=False,
    )
    PaymentVerificationSummaryFactory(payment_plan=pp)
    return pp


@pytest.fixture
def service(payment_plan: PaymentPlan) -> XlsxPaymentPlanDeliveryImportService:
    return XlsxPaymentPlanDeliveryImportService(payment_plan, io.BytesIO())


@pytest.fixture
def payment(payment_plan):
    return PaymentFactory(parent=payment_plan)


@pytest.fixture
def payment_verification_plan(payment_plan):
    return PaymentVerificationPlanFactory(payment_plan=payment_plan)


@pytest.fixture
def received_verification(payment_verification_plan, payment):
    return PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED,
        received_amount=Decimal("100.00"),
    )


@pytest.fixture
def pending_verification(payment_verification_plan, payment):
    return PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_PENDING,
    )


@pytest.fixture
def pending_payment(payment_plan):
    return PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_PENDING,
        delivered_quantity=None,
        delivered_quantity_usd=None,
        entitlement_quantity=Decimal("100.00"),
        delivery_date=datetime.datetime(2024, 3, 10, 8, 0, 0, tzinfo=UTC),
    )


@pytest.fixture
def service_with_payment(pending_payment, payment_plan):
    return XlsxPaymentPlanDeliveryImportService(payment_plan, io.BytesIO())


def _make_row_cells(values: list) -> list:
    """Create mock cells simulating openpyxl row."""
    cells = []
    for val in values:
        cell = MagicMock()
        cell.value = val
        cells.append(cell)
    return cells


# --- _set_payment_delivery_date ---


def test_set_payment_delivery_date_parses_string(service):
    payment = MagicMock()
    payment.delivery_date = None
    delivery_date, payment_delivery_date = service._set_payment_delivery_date("2024-01-15", payment)
    assert delivery_date.tzinfo is not None  # should be UTC-localized
    assert delivery_date.year == 2024
    assert delivery_date.month == 1
    assert delivery_date.day == 15
    assert payment_delivery_date is None


def test_set_payment_delivery_date_naive_datetime(service):
    naive_dt = datetime.datetime(2024, 6, 15, 12, 0, 0)
    payment = MagicMock()
    payment.delivery_date = None
    delivery_date, payment_delivery_date = service._set_payment_delivery_date(naive_dt, payment)
    assert delivery_date.tzinfo is not None
    assert delivery_date.tzinfo == pytz.utc
    assert payment_delivery_date is None


def test_set_payment_delivery_date_aware_datetime(service):
    aware_dt = datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
    payment = MagicMock()
    payment.delivery_date = None
    delivery_date, payment_delivery_date = service._set_payment_delivery_date(aware_dt, payment)
    assert delivery_date.tzinfo is not None
    assert payment_delivery_date is None


def test_set_payment_delivery_date_with_existing_payment_date(service):
    existing_date = datetime.datetime(2024, 3, 10, 8, 0, 0, tzinfo=UTC)
    payment = MagicMock()
    payment.delivery_date = existing_date
    delivery_date, payment_delivery_date = service._set_payment_delivery_date("2024-06-15", payment)
    assert payment_delivery_date is not None
    assert payment_delivery_date.tzinfo is None  # replace(tzinfo=None)


# --- _get_values_for_update ---


def test_get_values_for_update_all_headers(service):
    service.xlsx_headers = [
        "payment_id",
        "delivered_quantity",
        "delivery_date",
        "reference_id",
        "reason_for_unsuccessful_payment",
        "additional_collector_name",
        "transaction_status_blockchain_link",
        "additional_document_type",
        "additional_document_number",
    ]
    row = _make_row_cells(
        [
            "PAY-001",  # payment_id
            "100.00",  # delivered_quantity
            "2024-06-15",  # delivery_date
            "REF-123",  # reference_id
            "Bank closed",  # reason
            "John Doe",  # additional_collector_name
            "https://link",  # transaction_status_blockchain_link
            "Passport",  # additional_document_type
            "DOC-456",  # additional_document_number
        ]
    )
    result = service._get_values_for_update(row)
    # Returns: (additional_collector_name, additional_document_number, additional_document_type,
    #           delivery_date, reason, reference_id, transaction_status_blockchain_link)
    (
        additional_collector_name,
        additional_document_number,
        additional_document_type,
        delivery_date,
        reason,
        reference_id,
        transaction_status_blockchain_link,
    ) = result
    assert additional_collector_name == "John Doe"
    assert additional_document_number == "DOC-456"
    assert additional_document_type == "Passport"
    assert delivery_date == "2024-06-15"
    assert reason == "Bank closed"
    assert reference_id == "REF-123"
    assert transaction_status_blockchain_link == "https://link"


def test_get_values_for_update_no_optional_headers(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells(["PAY-001", "100.00"])
    result = service._get_values_for_update(row)
    (
        additional_collector_name,
        additional_document_number,
        additional_document_type,
        delivery_date,
        reason,
        reference_id,
        transaction_status_blockchain_link,
    ) = result
    assert delivery_date is None
    assert reference_id is None
    assert reason is None
    assert additional_collector_name is None
    assert transaction_status_blockchain_link is None
    assert additional_document_number is None
    assert additional_document_type is None


# --- _get_additional_doc_values ---


def test_get_additional_doc_values_present(service):
    service.xlsx_headers = ["payment_id", "additional_document_type", "additional_document_number"]
    row = _make_row_cells(["PAY-001", "ID Card", "DOC-789"])
    number, doc_type = service._get_additional_doc_values(row)
    assert doc_type == "ID Card"
    assert number == "DOC-789"


def test_get_additional_doc_values_absent(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells(["PAY-001", "100.00"])
    number, doc_type = service._get_additional_doc_values(row)
    assert doc_type is None
    assert number is None


# --- _update_payment_verification ---


def test_update_payment_verification_received(service, payment, received_verification):
    service._update_payment_verification(payment, Decimal("100.00"))
    assert len(service.payment_verifications_to_save) == 1
    assert service.payment_verifications_to_save[0].status == PaymentVerification.STATUS_RECEIVED


def test_update_payment_verification_not_received(service, payment, received_verification):
    service._update_payment_verification(payment, Decimal(0))
    assert service.payment_verifications_to_save[-1].status == PaymentVerification.STATUS_NOT_RECEIVED


def test_update_payment_verification_received_with_issues(service, payment, received_verification):
    service._update_payment_verification(payment, Decimal("50.00"))
    assert service.payment_verifications_to_save[-1].status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES


def test_update_payment_verification_pending_skipped(service, payment, pending_verification):
    initial_count = len(service.payment_verifications_to_save)
    service._update_payment_verification(payment, Decimal("100.00"))
    assert len(service.payment_verifications_to_save) == initial_count  # no change


# --- _get_optional_cell_value ---


def test_get_optional_cell_value_present(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity", "reference_id"]
    row = _make_row_cells(["PAY-001", "100.00", "REF-999"])
    result = service._get_optional_cell_value(row, "reference_id")
    assert result == "REF-999"


def test_get_optional_cell_value_absent(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells(["PAY-001", "100.00"])
    result = service._get_optional_cell_value(row, "reference_id")
    assert result is None


# --- _update_payment_verification: delivered_quantity is None ---


def test_update_payment_verification_delivered_none(service, payment, received_verification):
    service._update_payment_verification(payment, None)
    assert len(service.payment_verifications_to_save) >= 1
    assert service.payment_verifications_to_save[-1].status == PaymentVerification.STATUS_NOT_RECEIVED


# --- _update_payment_verification: no verification exists ---


def test_update_payment_verification_no_verification(service, payment):
    # No PaymentVerification created for this payment
    initial_count = len(service.payment_verifications_to_save)
    service._update_payment_verification(payment, Decimal("100.00"))
    assert len(service.payment_verifications_to_save) == initial_count  # nothing added


# --- _validate_headers ---


def test_validate_headers_appends_error_when_required_column_missing(service):
    service.sheetname = "Payment Plan - Payment List"
    service.xlsx_headers = ["payment_id", "delivery_date"]
    service._validate_headers()
    assert len(service.errors) == 1
    assert "are required headers" in service.errors[0].message


# --- _validate_payment_id ---


def test_validate_payment_id_appends_error_for_unknown_id(service):
    service.sheetname = "Payment Plan - Payment List"
    service.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells(["PP-0060-UNKNOWN", 100])
    service._validate_payment_id(row)
    assert len(service.errors) == 1
    assert "is not in Payment Plan Payment List" in service.errors[0].message


# --- _validate_delivered_quantity ---


def test_validate_delivered_quantity_returns_when_payment_unknown(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells(["PP-0060-UNKNOWN", 100])
    service._validate_delivered_quantity(row)
    assert service.errors == []
    assert service.is_updated is False


# --- _validate_reason_for_unsuccessful_payment ---


def test_validate_reason_for_unsuccessful_payment_returns_when_payment_unknown(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity", "reason_for_unsuccessful_payment"]
    row = _make_row_cells(["PP-0060-UNKNOWN", 100, "Bank closed"])
    service._validate_reason_for_unsuccessful_payment(row)
    assert service.is_updated is False


def test_validate_reason_for_unsuccessful_payment_marks_updated_on_change(service_with_payment, pending_payment):
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity", "reason_for_unsuccessful_payment"]
    row = _make_row_cells([str(pending_payment.unicef_id), 100, "Bank closed"])
    service_with_payment._validate_reason_for_unsuccessful_payment(row)
    assert service_with_payment.is_updated is True


def test_validate_reason_for_unsuccessful_payment_keeps_not_updated_when_unchanged(
    service_with_payment, pending_payment
):
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity", "reason_for_unsuccessful_payment"]
    row = _make_row_cells([str(pending_payment.unicef_id), 100, pending_payment.reason_for_unsuccessful_payment])
    service_with_payment._validate_reason_for_unsuccessful_payment(row)
    assert service_with_payment.is_updated is False


# --- _validate_delivery_date ---


def test_validate_delivery_date_returns_when_payment_unknown(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity", "delivery_date"]
    row = _make_row_cells(["PP-0060-UNKNOWN", 100, "2024-06-15"])
    service._validate_delivery_date(row)
    assert service.errors == []
    assert service.is_updated is False


def test_validate_delivery_date_appends_error_for_future_date(service_with_payment, pending_payment):
    service_with_payment.sheetname = "Payment Plan - Payment List"
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity", "delivery_date"]
    future_date = datetime.datetime.now(tz=UTC) + datetime.timedelta(days=30)
    row = _make_row_cells([str(pending_payment.unicef_id), 100, future_date])
    service_with_payment._validate_delivery_date(row)
    assert len(service_with_payment.errors) == 1
    assert "cannot be greater than today's date" in service_with_payment.errors[0].message


# --- _validate_reference_id ---


def test_validate_reference_id_returns_when_payment_unknown(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity", "reference_id"]
    row = _make_row_cells(["PP-0060-UNKNOWN", 100, "REF-123"])
    service._validate_reference_id(row)
    assert service.is_updated is False


# --- _import_row ---


def test_import_row_resets_delivery_date_for_zero_delivered_quantity(service_with_payment, pending_payment):
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells([str(pending_payment.unicef_id), 0])

    service_with_payment._import_row(row, 1.0)

    assert len(service_with_payment.payments_to_save) == 1
    updated_payment = service_with_payment.payments_to_save[0]
    assert updated_payment.status == Payment.STATUS_NOT_DISTRIBUTED
    assert updated_payment.delivered_quantity == 0
    assert updated_payment.delivery_date is None
