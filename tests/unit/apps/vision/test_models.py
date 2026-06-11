import pytest

from extras.test_utils.factories.account import UserFactory
from hope.contrib.vision.fixtures import FundsCommitmentFactory
from hope.contrib.vision.models import (
    DownPayment,
    FundsCommitment,
    FundsCommitmentGroup,
    FundsCommitmentItem,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(afghanistan):
    return UserFactory()


def test_trigger_creates_rows(afghanistan, user) -> None:
    assert FundsCommitmentGroup.objects.count() == 0
    assert FundsCommitmentItem.objects.count() == 0

    FundsCommitmentFactory(funds_commitment_number="123")

    assert FundsCommitmentGroup.objects.count() == 1
    assert FundsCommitmentItem.objects.count() == 1

    FundsCommitmentFactory(funds_commitment_number="123")

    assert FundsCommitmentGroup.objects.count() == 1
    assert FundsCommitmentItem.objects.count() == 2

    FundsCommitmentFactory(funds_commitment_number="345")

    assert FundsCommitmentGroup.objects.count() == 2
    assert FundsCommitmentItem.objects.count() == 3

    fcg = FundsCommitmentGroup.objects.get(funds_commitment_number="123")
    assert fcg.funds_commitment_items.count() == 2

    fcg = FundsCommitmentGroup.objects.get(funds_commitment_number="345")
    assert fcg.funds_commitment_items.count() == 1


def test_funds_commitment_group_str(afghanistan) -> None:
    fcg = FundsCommitmentGroup.objects.create(funds_commitment_number="FC-001")
    assert str(fcg) == "FC-001"


def test_funds_commitment_item_str(afghanistan) -> None:
    fcg = FundsCommitmentGroup.objects.create(funds_commitment_number="FC-001")
    fci = FundsCommitmentItem.objects.create(
        funds_commitment_group=fcg,
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
    fcg = FundsCommitmentGroup.objects.create(funds_commitment_number="FC-001")
    fci = FundsCommitmentItem.objects.create(
        funds_commitment_group=fcg,
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
