from datetime import date
from decimal import Decimal

import pytest

from extras.test_utils.factories.account import UserFactory
from hope.contrib.vision.fixtures import FundsCommitmentFactory
from hope.contrib.vision.models import (
    DownPayment,
    FundsCommitment,
    FundsCommitmentHeader,
    FundsCommitmentItem,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(afghanistan):
    return UserFactory()


def test_trigger_creates_rows(afghanistan, user) -> None:
    assert FundsCommitmentHeader.objects.count() == 0
    assert FundsCommitmentItem.objects.count() == 0

    FundsCommitmentFactory(funds_commitment_number="123")

    assert FundsCommitmentHeader.objects.count() == 1
    assert FundsCommitmentItem.objects.count() == 1

    FundsCommitmentFactory(funds_commitment_number="123")

    assert FundsCommitmentHeader.objects.count() == 1
    assert FundsCommitmentItem.objects.count() == 2

    FundsCommitmentFactory(funds_commitment_number="345")

    assert FundsCommitmentHeader.objects.count() == 2
    assert FundsCommitmentItem.objects.count() == 3

    header = FundsCommitmentHeader.objects.get(funds_commitment_number="123")
    assert header.funds_commitment_items.count() == 2

    header = FundsCommitmentHeader.objects.get(funds_commitment_number="345")
    assert header.funds_commitment_items.count() == 1


def test_funds_commitment_header_str(afghanistan) -> None:
    header = FundsCommitmentHeader.objects.create(funds_commitment_number="FC-001")
    assert str(header) == "FC-001"


def test_funds_commitment_header_labels() -> None:
    assert FundsCommitmentHeader._meta.verbose_name == "Funds Commitment Header"
    assert FundsCommitmentHeader._meta.verbose_name_plural == "Funds Commitment Headers"


@pytest.fixture
def header_with_multiple_commitments(afghanistan) -> FundsCommitmentHeader:
    FundsCommitmentFactory(
        rec_serial_number=200,
        funds_commitment_number="FC-002",
        vendor_id="VENDOR-2",
        posting_date=date(2026, 9, 2),
        document_reference="REFERENCE-2",
        fc_status="C",
        currency_code="EUR",
        commitment_amount_local=Decimal("250.75"),
        commitment_amount_usd=Decimal("300.50"),
    )
    FundsCommitmentFactory(
        rec_serial_number=100,
        funds_commitment_number="FC-002",
        vendor_id="VENDOR-1",
        posting_date=date(2026, 9, 1),
        document_reference="REFERENCE-1",
        fc_status="O",
        currency_code="USD",
        commitment_amount_local=Decimal("100.25"),
        commitment_amount_usd=Decimal("100.50"),
    )
    return FundsCommitmentHeader.objects.get(funds_commitment_number="FC-002")


def test_funds_commitment_header_derived_fields(
    header_with_multiple_commitments: FundsCommitmentHeader,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(1):
        header = FundsCommitmentHeader.objects.with_derived_fields().get(pk=header_with_multiple_commitments.pk)

        assert header.rec_serial_number == 100
        assert header.vendor_id == "VENDOR-1"
        assert header.posting_date == date(2026, 9, 1)
        assert header.document_reference == "REFERENCE-1"
        assert header.fc_status == "O"
        assert header.total_amount_usd == Decimal("401.00")
        assert header.total_amount_local == Decimal("351.00")
        assert header.currency == "USD"


def test_funds_commitment_item_str(afghanistan) -> None:
    header = FundsCommitmentHeader.objects.create(funds_commitment_number="FC-001")
    fci = FundsCommitmentItem.objects.create(
        funds_commitment_header=header,
        rec_serial_number=12345,
        funds_commitment_item="001",
    )
    assert str(fci) == "FC-001 - 001"


def test_funds_commitment_str(afghanistan) -> None:
    fc = FundsCommitment.objects.create(
        rec_serial_number=67890,
        funds_commitment_number="FC-002",
    )
    assert str(fc) == "FC-002"


def test_down_payment_str(afghanistan) -> None:
    dp = DownPayment.objects.create(
        rec_serial_number=99999,
        business_area="BA01",
        down_payment_reference="DP-REF-001",
        document_type="DO",
        consumed_fc_number="FC-001",
        total_down_payment_amount_local=1000.00,
    )
    assert str(dp) == "99999"


def test_funds_commitment_str_no_number(afghanistan) -> None:
    fc = FundsCommitment.objects.create(
        rec_serial_number=67890,
        funds_commitment_number="",
    )
    assert str(fc) == ""


def test_funds_commitment_item_str_all_nulls(afghanistan) -> None:
    header = FundsCommitmentHeader.objects.create(funds_commitment_number="FC-001")
    fci = FundsCommitmentItem.objects.create(
        funds_commitment_header=header,
        rec_serial_number=12345,
        funds_commitment_item="001",
        vendor_id=None,
        business_area=None,
        posting_date=None,
        vision_approval=None,
        document_reference=None,
        fc_status=None,
        wbs_element=None,
        grant_number=None,
        document_type=None,
        document_text=None,
        currency_code=None,
        gl_account=None,
        commitment_amount_local=None,
        commitment_amount_usd=None,
        total_open_amount_local=None,
        total_open_amount_usd=None,
        sponsor=None,
        sponsor_name=None,
        fund=None,
        funds_center=None,
        percentage=None,
        created_by=None,
        updated_by=None,
        office=None,
    )
    assert str(fci) == "FC-001 - 001"
