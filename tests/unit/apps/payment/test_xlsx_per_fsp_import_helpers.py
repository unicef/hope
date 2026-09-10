"""Tests for XlsxPaymentPlanDeliveryImportService extracted helpers."""

import datetime
from datetime import UTC
from decimal import Decimal
import io
from unittest.mock import MagicMock

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentPlanFactory,
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
        status=PaymentPlan.Status.ACCEPTED,
        create_payment_verification_summary=False,
    )
    PaymentVerificationSummaryFactory(payment_plan=pp)
    return pp


@pytest.fixture
def service(payment_plan: PaymentPlan) -> XlsxPaymentPlanDeliveryImportService:
    return XlsxPaymentPlanDeliveryImportService(payment_plan, io.BytesIO())


@pytest.fixture
def sent_to_fsp_payment(payment_plan):
    return PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_SENT_TO_FSP,
        delivered_quantity=None,
        delivered_quantity_usd=None,
        entitlement_quantity=Decimal("100.00"),
        delivery_date=datetime.datetime(2024, 3, 10, 8, 0, 0, tzinfo=UTC),
    )


@pytest.fixture
def service_with_payment(sent_to_fsp_payment, payment_plan):
    return XlsxPaymentPlanDeliveryImportService(payment_plan, io.BytesIO())


@pytest.fixture
def reconciled_payment(payment_plan):
    return PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_DISTRIBUTION_PARTIAL,
        delivered_quantity=Decimal("50.00"),
        entitlement_quantity=Decimal("100.00"),
    )


@pytest.fixture
def service_with_reconciled_payment(reconciled_payment, payment_plan):
    return XlsxPaymentPlanDeliveryImportService(payment_plan, io.BytesIO())


def _make_row_cells(values: list) -> list:
    """Create mock cells simulating openpyxl row."""
    cells = []
    for val in values:
        cell = MagicMock()
        cell.value = val
        cells.append(cell)
    return cells


def test_init_rejects_unsupported_null_delivery_policy(payment_plan, django_assert_num_queries):
    with django_assert_num_queries(0), pytest.raises(ValueError, match="Unsupported null delivery policy"):
        XlsxPaymentPlanDeliveryImportService(payment_plan, io.BytesIO(), null_delivery_policy="unsupported")


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


def test_validate_payment_id_records_known_id(service_with_payment, sent_to_fsp_payment, django_assert_num_queries):
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity"]
    payment_id = str(sent_to_fsp_payment.unicef_id)
    row = _make_row_cells([payment_id, 100])

    with django_assert_num_queries(0):
        service_with_payment._validate_payment_id(row)

    assert service_with_payment.payment_ids_from_xlsx == [payment_id]
    assert service_with_payment.errors == []


def test_validate_payment_id_does_not_record_null_id(service, django_assert_num_queries):
    service.sheetname = "Payment Plan - Payment List"
    service.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells([None, 100])

    with django_assert_num_queries(0):
        service._validate_payment_id(row)

    assert len(service.errors) == 1
    assert service.payment_ids_from_xlsx == []


def test_should_skip_row_with_null_payment_id(service, django_assert_num_queries):
    with django_assert_num_queries(0):
        result = service._should_skip_row(None)

    assert result is True


def test_should_skip_row_from_closed_plan(service_with_payment, sent_to_fsp_payment, django_assert_num_queries):
    service_with_payment.payment_plan.status = PaymentPlan.Status.CLOSED

    with django_assert_num_queries(0):
        result = service_with_payment._should_skip_row(str(sent_to_fsp_payment.unicef_id))

    assert result is True


def test_should_skip_row_with_unknown_payment(service, django_assert_num_queries):
    with django_assert_num_queries(0):
        result = service._should_skip_row("UNKNOWN")

    assert result is True


def test_get_row_action_skips_closed_plan(service_with_payment, sent_to_fsp_payment, django_assert_num_queries):
    service_with_payment.payment_plan.status = PaymentPlan.Status.CLOSED

    with django_assert_num_queries(0):
        action = service_with_payment._get_row_action(sent_to_fsp_payment, Decimal("100.00"))

    assert action == service_with_payment.ACTION_SKIP


def test_get_row_action_skips_ineligible_override_status(
    service_with_payment, sent_to_fsp_payment, django_assert_num_queries
):
    service_with_payment.override = True
    sent_to_fsp_payment.status = Payment.STATUS_MANUALLY_CANCELLED

    with django_assert_num_queries(0):
        action = service_with_payment._get_row_action(sent_to_fsp_payment, Decimal("100.00"))

    assert action == service_with_payment.ACTION_SKIP


def test_get_row_action_applies_first_reconciliation(
    service_with_payment, sent_to_fsp_payment, django_assert_num_queries
):
    with django_assert_num_queries(0):
        action = service_with_payment._get_row_action(sent_to_fsp_payment, Decimal("100.00"))

    assert action == service_with_payment.ACTION_APPLY


def test_get_row_action_skips_normal_payment_that_was_not_sent_to_fsp(
    service_with_payment, sent_to_fsp_payment, django_assert_num_queries
):
    sent_to_fsp_payment.status = Payment.STATUS_MANUALLY_CANCELLED

    with django_assert_num_queries(0):
        action = service_with_payment._get_row_action(sent_to_fsp_payment, Decimal("100.00"))

    assert action == service_with_payment.ACTION_SKIP


def test_parse_delivered_quantity_rejects_unquantizable_number(service, django_assert_num_queries):
    with django_assert_num_queries(0), pytest.raises(ValueError, match="^$"):
        service._parse_delivered_quantity(Decimal("1E+999999"))


# --- _validate_delivered_quantity ---


def test_validate_delivered_quantity_returns_when_payment_unknown(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells(["PP-0060-UNKNOWN", 100])
    service._validate_delivered_quantity(row)
    assert service.errors == []
    assert service.is_updated is False


# --- _validate_delivery_date ---


def test_validate_delivery_date_returns_when_payment_unknown(service):
    service.xlsx_headers = ["payment_id", "delivered_quantity", "delivery_date"]
    row = _make_row_cells(["PP-0060-UNKNOWN", 100, "2024-06-15"])
    service._validate_delivery_date(row)
    assert service.errors == []
    assert service.is_updated is False


def test_validate_delivery_date_appends_error_for_future_date(service_with_payment, sent_to_fsp_payment):
    service_with_payment.sheetname = "Payment Plan - Payment List"
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity", "delivery_date"]
    future_date = datetime.datetime.now(tz=UTC) + datetime.timedelta(days=30)
    row = _make_row_cells([str(sent_to_fsp_payment.unicef_id), 100, future_date])
    service_with_payment._validate_delivery_date(row)
    assert len(service_with_payment.errors) == 1
    assert "cannot be greater than today's date" in service_with_payment.errors[0].message


def test_validate_delivery_date_ignores_empty_cell(
    service_with_payment, sent_to_fsp_payment, django_assert_num_queries
):
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity", "delivery_date"]
    row = _make_row_cells([str(sent_to_fsp_payment.unicef_id), 100, None])

    with django_assert_num_queries(0):
        service_with_payment._validate_delivery_date(row)

    assert service_with_payment.errors == []


# --- _import_row ---


def test_import_row_preserves_delivery_date_when_header_is_missing(service_with_payment, sent_to_fsp_payment):
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells([str(sent_to_fsp_payment.unicef_id), 0])

    service_with_payment._import_row(row, 1.0)

    assert len(service_with_payment.payments_to_save) == 1
    updated_payment = service_with_payment.payments_to_save[0]
    assert updated_payment.status == Payment.STATUS_NOT_DISTRIBUTED
    assert updated_payment.delivered_quantity == 0
    assert updated_payment.delivery_date == sent_to_fsp_payment.delivery_date


def test_import_row_rejects_invalid_quantity(service_with_payment, sent_to_fsp_payment, django_assert_num_queries):
    service_with_payment.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells([str(sent_to_fsp_payment.unicef_id), "invalid"])

    with (
        django_assert_num_queries(0),
        pytest.raises(
            XlsxPaymentPlanDeliveryImportService.XlsxPaymentPlanDeliveryImportServiceError,
            match="Invalid delivered_quantity",
        ),
    ):
        service_with_payment._import_row(row, 1.0)


def test_import_row_rejects_quantity_conflict(
    service_with_reconciled_payment, reconciled_payment, django_assert_num_queries
):
    service_with_reconciled_payment.xlsx_headers = ["payment_id", "delivered_quantity"]
    row = _make_row_cells([str(reconciled_payment.unicef_id), Decimal("40.00")])

    with (
        django_assert_num_queries(0),
        pytest.raises(
            XlsxPaymentPlanDeliveryImportService.XlsxPaymentPlanDeliveryImportServiceError,
            match="Delivered quantity conflict",
        ),
    ):
        service_with_reconciled_payment._import_row(row, 1.0)


def test_validate_stops_after_header_error(service, django_assert_num_queries):
    service.sheetname = "Payment Plan - Payment List"
    service.xlsx_headers = ["payment_id"]

    with django_assert_num_queries(0):
        service.validate()

    assert len(service.errors) == 1
