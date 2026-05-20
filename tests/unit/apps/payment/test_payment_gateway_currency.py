from unittest.mock import MagicMock

import pytest

from extras.test_utils.factories import CurrencyFactory
from hope.apps.payment.services.payment_gateway import PaymentInstructionFromSplitSerializer


@pytest.fixture
def usd(db):
    return CurrencyFactory(code="USD", name="United States Dollar")


@pytest.fixture
def usd_with_overridden_vision_code(db):
    return CurrencyFactory(code="USD", name="United States Dollar", vision_code="USC")


class TestPaymentInstructionFromSplitSerializerCurrency:
    def test_payload_destination_currency_is_string(self, usd, django_assert_num_queries):
        payment_plan = MagicMock()
        payment_plan.currency = usd
        payment_plan.business_area.code = "BA01"
        payment_plan.business_area.payment_countries.count.return_value = 0

        split = MagicMock()
        split.payment_plan = payment_plan
        split.payment_plan.delivery_mechanism.code = "cash"

        serializer = PaymentInstructionFromSplitSerializer(split, context={"user_email": "test@example.com"})
        with django_assert_num_queries(0):
            payload = serializer.data["payload"]

        assert payload["destination_currency"] == "USD"
        assert isinstance(payload["destination_currency"], str)

    def test_payload_destination_currency_none_when_no_currency(self, django_assert_num_queries):
        payment_plan = MagicMock()
        payment_plan.currency = None
        payment_plan.business_area.code = "BA01"
        payment_plan.business_area.payment_countries.count.return_value = 0

        split = MagicMock()
        split.payment_plan = payment_plan
        split.payment_plan.delivery_mechanism.code = "cash"

        serializer = PaymentInstructionFromSplitSerializer(split, context={"user_email": "test@example.com"})
        with django_assert_num_queries(0):
            payload = serializer.data["payload"]

        assert payload["destination_currency"] is None

    def test_payload_destination_currency_uses_vision_code_when_overridden(self, django_assert_num_queries):
        currency = CurrencyFactory(code="XYC", name="Test Currency", vision_code="XYCO")
        payment_plan = MagicMock()
        payment_plan.currency = currency
        payment_plan.business_area.code = "BA01"
        payment_plan.business_area.payment_countries.count.return_value = 0

        split = MagicMock()
        split.payment_plan = payment_plan
        split.payment_plan.delivery_mechanism.code = "cash"

        serializer = PaymentInstructionFromSplitSerializer(split, context={"user_email": "test@example.com"})
        with django_assert_num_queries(0):
            payload = serializer.data["payload"]

        assert payload["destination_currency"] == "XYCO"
        assert payload["destination_currency"] != currency.code
