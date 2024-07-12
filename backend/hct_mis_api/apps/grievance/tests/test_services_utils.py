from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.geo.fixtures import CountryFactory
from hct_mis_api.apps.grievance.services.data_change.utils import (
    cast_flex_fields,
    handle_add_document,
    handle_add_payment_channel,
    handle_role,
    handle_update_payment_channel,
    to_phone_number_str,
    verify_flex_fields,
)
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    DocumentTypeFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    BankAccountInfo,
    Document,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.utils.models import MergeStatusModel


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

    def test_handle_role(self) -> None:
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        household, individuals = create_household_and_individuals(
            household_data={"business_area": business_area},
            individuals_data=[{}],
        )

        self.assertEqual(IndividualRoleInHousehold.objects.all().count(), 0)
        with pytest.raises(ValidationError) as e:
            IndividualRoleInHouseholdFactory(household=household, individual=individuals[0], role=ROLE_PRIMARY)
            handle_role(ROLE_PRIMARY, household, individuals[0])
            assert str(e.value) == "Ticket cannot be closed, primary collector role has to be reassigned"

        # just remove exists roles
        IndividualRoleInHousehold.objects.filter(household=household).update(role=ROLE_ALTERNATE)
        handle_role("OTHER_ROLE_XD", household, individuals[0])
        self.assertEqual(IndividualRoleInHousehold.objects.filter(household=household).count(), 0)

        # create new role
        handle_role(ROLE_ALTERNATE, household, individuals[0])
        role = IndividualRoleInHousehold.objects.filter(household=household).first()
        self.assertEqual(role.role, ROLE_ALTERNATE)
        self.assertEqual(role.rdi_merge_status, MergeStatusModel.MERGED)

    def test_handle_add_document(self) -> None:
        create_afghanistan()
        country = CountryFactory(name="Afghanistan")
        document_type = DocumentTypeFactory(key="TAX", label="tax")
        business_area = BusinessArea.objects.get(slug="afghanistan")
        household, individuals = create_household_and_individuals(
            household_data={"business_area": business_area},
            individuals_data=[{}],
        )
        individual = individuals[0]
        document_data = {"key": "TAX", "country": "AFG", "number": "111", "photo": "photo", "photoraw": "photo_raw"}

        with pytest.raises(ValidationError) as e:
            DocumentFactory(
                document_number=111,
                type=document_type,
                country=country,
                program_id=individual.program_id,
                status=Document.STATUS_VALID,
            )
            handle_add_document(document_data, individual)
            assert str(e.value) == "Document with number 111 of type tax already exists"

        with pytest.raises(ValidationError) as e:
            document_type.unique_for_individual = True
            document_type.save()
            handle_add_document(document_data, individual)
            assert str(e.value) == "Document of type tax already exists for this individual"

        Document.objects.all().delete()
        self.assertEqual(Document.objects.all().count(), 0)

        document = handle_add_document(document_data, individual)
        self.assertIsInstance(document, Document)
        self.assertEqual(document.rdi_merge_status, MergeStatusModel.MERGED)
