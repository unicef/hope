from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.grievance.services.data_change.utils import (
    cast_flex_fields,
    handle_add_payment_channel,
    handle_update_payment_channel,
    to_phone_number_str,
    verify_flex_fields,
)
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import BankAccountInfo


class FlexibleAttribute:
    class objects:
        @staticmethod
        def filter(type: Any) -> Any:
            return MagicMock()


@pytest.mark.django_db
class TestGrievanceUtils(TestCase):
    def test_to_phone_number_str(self) -> None:
        data = {"phone_number": 123456789}
        to_phone_number_str(data, "phone_number")
        self.assertEqual(data["phone_number"], "123456789")

        data = {"phone_number": 123456789}
        to_phone_number_str(data, "other_field_name")
        self.assertEqual(data["phone_number"], 123456789)

    @patch("hct_mis_api.apps.core.models.FlexibleAttribute.objects.filter")
    def test_cast_flex_fields(self, mock_filter: Any) -> None:
        mock_filter.side_effect = [
            MagicMock(values_list=MagicMock(return_value=["decimal_field"])),
            MagicMock(values_list=MagicMock(return_value=["integer_field"])),
        ]

        flex_fields = {"decimal_field": "321.11", "integer_field": "123", "string_field": "some_string"}
        cast_flex_fields(flex_fields)

        self.assertEqual(flex_fields["string_field"], "some_string")
        self.assertEqual(flex_fields["integer_field"], 123)
        self.assertEqual(flex_fields["decimal_field"], 321.11)

    def test_handle_add_payment_channel(self) -> None:
        business_area = BusinessAreaFactory(name="Afghanistan")
        payment_channel = {
            "type": "BANK_TRANSFER",
            "bank_name": "BankName",
            "bank_account_number": "12345678910",
        }
        individual = IndividualFactory(household=None, business_area=business_area)
        obj = handle_add_payment_channel(payment_channel, individual)

        self.assertIsInstance(obj, BankAccountInfo)

        payment_channel["type"] = "OTHER"
        resp_none = handle_add_payment_channel(payment_channel, individual)
        self.assertIsNone(resp_none)

    def test_handle_update_payment_channel(self) -> None:
        business_area = BusinessAreaFactory(name="Afghanistan")
        individual = IndividualFactory(household=None, business_area=business_area)
        bank_info = BankAccountInfoFactory(individual=individual)
        id_str = encode_id_base64_required(str(bank_info.pk), "BankAccountInfo")

        payment_channel_dict = {
            "type": "BANK_TRANSFER",
            "id": id_str,
            "bank_name": "BankName",
            "bank_account_number": "1234321",
        }

        obj = handle_update_payment_channel(payment_channel_dict)
        self.assertIsInstance(obj, BankAccountInfo)
        payment_channel_dict["type"] = "OTHER"
        resp_none = handle_update_payment_channel(payment_channel_dict)
        self.assertIsNone(resp_none)

    def test_verify_flex_fields(self) -> None:
        with pytest.raises(ValueError) as e:
            verify_flex_fields({"key": "value"}, "associated_with")
            assert str(e.value) == "associated_with argument must be one of ['household', 'individual']"

        with pytest.raises(ValueError) as e:
            verify_flex_fields({"key": "value"}, "individuals")
            assert str(e.value) == "key is not a correct `flex field"
