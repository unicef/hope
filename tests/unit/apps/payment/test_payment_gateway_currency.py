from unittest.mock import MagicMock

import pytest

from extras.test_utils.factories import CurrencyFactory
from hope.apps.payment.services.payment_gateway import (
    PaymentInstructionFromSplitSerializer,
    PaymentSerializer,
)


@pytest.fixture
def usd(db):
    return CurrencyFactory(code="USD", name="United States Dollar")


class TestPaymentInstructionFromSplitSerializerCurrency:
    def test_payload_destination_currency_is_string(self, usd, django_assert_num_queries):
        payment_plan = MagicMock()
        payment_plan.currency = usd
        payment_plan.business_area.code = "BA01"
        payment_plan.business_area.payment_countries.count.return_value = 0

        split = MagicMock()
        split.payment_plan = payment_plan
        split.delivery_mechanism.code = "cash"

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
        split.delivery_mechanism.code = "cash"

        serializer = PaymentInstructionFromSplitSerializer(split, context={"user_email": "test@example.com"})
        with django_assert_num_queries(0):
            payload = serializer.data["payload"]

        assert payload["destination_currency"] is None


class TestPaymentSerializerCurrency:
    def test_payload_destination_currency_is_string(self, usd, django_assert_num_queries):
        snapshot_data = {
            "primary_collector": {
                "unicef_id": "IND-001",
                "phone_no": "123",
                "family_name": "Doe",
                "given_name": "John",
                "full_name": "John Doe",
                "middle_name": "",
                "account_data": {},
            }
        }

        payment = MagicMock()
        payment.currency = usd
        payment.entitlement_quantity = 100.00
        payment.delivery_type.code = "cash"
        payment.delivery_type.account_type = None
        payment.household_snapshot.snapshot_data = snapshot_data

        serializer = PaymentSerializer(payment)
        with django_assert_num_queries(0):
            payload = serializer.data["payload"]

        assert payload["destination_currency"] == "USD"
        assert isinstance(payload["destination_currency"], str)

    def test_payload_destination_currency_none_when_no_currency(self, django_assert_num_queries):
        snapshot_data = {
            "primary_collector": {
                "unicef_id": "IND-001",
                "phone_no": "123",
                "family_name": "Doe",
                "given_name": "John",
                "full_name": "John Doe",
                "middle_name": "",
                "account_data": {},
            }
        }

        payment = MagicMock()
        payment.currency = None
        payment.entitlement_quantity = 100.00
        payment.delivery_type.code = "cash"
        payment.delivery_type.account_type = None
        payment.household_snapshot.snapshot_data = snapshot_data

        with django_assert_num_queries(0):
            PaymentSerializer(payment)

        payload_data = {
            "amount": payment.entitlement_quantity,
            "destination_currency": payment.currency.code if payment.currency else None,
            "delivery_mechanism": "cash",
        }
        assert payload_data["destination_currency"] is None
