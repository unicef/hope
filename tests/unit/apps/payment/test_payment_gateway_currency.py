from unittest.mock import MagicMock

import pytest

from hope.apps.payment.services.payment_gateway import PaymentInstructionFromSplitSerializer


@pytest.fixture
def build_split_mock():
    def _build(currency):
        payment_plan = MagicMock()
        payment_plan.currency = currency
        payment_plan.business_area.code = "BA01"
        payment_plan.business_area.payment_countries.count.return_value = 0
        payment_plan.business_area.payment_countries.first.return_value = None
        split = MagicMock()
        split.payment_plan = payment_plan
        split.payment_plan.delivery_mechanism.code = "cash"
        return split

    return _build


@pytest.mark.django_db
def test_instruction_payload_destination_currency_is_the_iso_code(build_split_mock, currency_syp):
    split = build_split_mock(currency_syp)

    payload = PaymentInstructionFromSplitSerializer(split, context={"user_email": "test@example.com"}).data["payload"]

    assert payload["destination_currency"] == "SYP"


@pytest.mark.django_db
def test_instruction_payload_destination_currency_is_none_when_no_currency(build_split_mock):
    split = build_split_mock(None)

    payload = PaymentInstructionFromSplitSerializer(split, context={"user_email": "test@example.com"}).data["payload"]

    assert payload["destination_currency"] is None
