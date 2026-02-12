"""Tests for XlsxPaymentPlanImportPerFspService extracted helpers."""

import datetime
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
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hope.models import (
    BusinessArea,
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
    return ProgramCycleFactory(program=program)


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
def service(payment_plan: PaymentPlan) -> XlsxPaymentPlanImportPerFspService:
    return XlsxPaymentPlanImportPerFspService(payment_plan, io.BytesIO())


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
    assert delivery_date.tzinfo == pytz.utc
    assert payment_delivery_date is None


def test_set_payment_delivery_date_aware_datetime(service):
    aware_dt = datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=pytz.utc)
    payment = MagicMock()
    payment.delivery_date = None
    delivery_date, payment_delivery_date = service._set_payment_delivery_date(aware_dt, payment)
    assert delivery_date.tzinfo is not None
    assert payment_delivery_date is None


def test_set_payment_delivery_date_with_existing_payment_date(service):
    existing_date = datetime.datetime(2024, 3, 10, 8, 0, 0, tzinfo=pytz.utc)
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


def test_update_payment_verification_received(service, payment_plan):
    payment = PaymentFactory(parent=payment_plan)
    pvp = PaymentVerificationPlanFactory(payment_plan=payment_plan)
    pv = PaymentVerificationFactory(  # noqa: F841
        payment_verification_plan=pvp,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED,
        received_amount=Decimal("100.00"),
    )
    service._update_payment_verification(payment, Decimal("100.00"))
    assert len(service.payment_verifications_to_save) == 1
    assert service.payment_verifications_to_save[0].status == PaymentVerification.STATUS_RECEIVED


def test_update_payment_verification_not_received(service, payment_plan):
    payment = PaymentFactory(parent=payment_plan)
    pvp = PaymentVerificationPlanFactory(payment_plan=payment_plan)
    pv = PaymentVerificationFactory(  # noqa: F841
        payment_verification_plan=pvp,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED,
        received_amount=Decimal("100.00"),
    )
    service._update_payment_verification(payment, Decimal(0))
    assert service.payment_verifications_to_save[-1].status == PaymentVerification.STATUS_NOT_RECEIVED


def test_update_payment_verification_received_with_issues(service, payment_plan):
    payment = PaymentFactory(parent=payment_plan)
    pvp = PaymentVerificationPlanFactory(payment_plan=payment_plan)
    pv = PaymentVerificationFactory(  # noqa: F841
        payment_verification_plan=pvp,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED,
        received_amount=Decimal("100.00"),
    )
    service._update_payment_verification(payment, Decimal("50.00"))
    assert service.payment_verifications_to_save[-1].status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES


def test_update_payment_verification_pending_skipped(service, payment_plan):
    payment = PaymentFactory(parent=payment_plan)
    pvp = PaymentVerificationPlanFactory(payment_plan=payment_plan)
    pv = PaymentVerificationFactory(  # noqa: F841
        payment_verification_plan=pvp,
        payment=payment,
        status=PaymentVerification.STATUS_PENDING,
    )
    initial_count = len(service.payment_verifications_to_save)
    service._update_payment_verification(payment, Decimal("100.00"))
    assert len(service.payment_verifications_to_save) == initial_count  # no change
