from unittest.mock import patch

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
    FieldFactory,
    get_core_fields_attributes,
)
from hct_mis_api.apps.core.field_attributes.fields_types import TYPE_STRING, Scope
from hct_mis_api.apps.payment.fixtures import generate_delivery_mechanisms


class TestCoreFields(APITestCase):
    def setUp(self) -> None:
        self.scopes = [Scope.GLOBAL, Scope.XLSX_PEOPLE]
        super().setUp()

    def test_all_fields_have_lookup(self) -> None:
        for field in get_core_fields_attributes():
            self.assertTrue(field.get("lookup"), f'{field.get("name")} does not have a lookup')

    @patch(
        "hct_mis_api.apps.core.field_attributes.core_fields_attributes.get_core_fields_attributes",
        lambda: [
            {
                "id": "b1f90314-b8b8-4bcb-9265-9d48d1fce5a4",
                "type": TYPE_STRING,
                "name": "given_name",
                "lookup": "given_name",
                "required": False,
                "label": {"English(EN)": "Given name"},
                "hint": "",
                "choices": [],
                "associated_with": "individual",
                "xlsx_field": "given_name_i_c",
                "scope": [Scope.GLOBAL, Scope.TARGETING, Scope.KOBO_IMPORT, Scope.INDIVIDUAL_UPDATE, Scope.XLSX_PEOPLE],
            },
            {
                "id": "b1f90314-b8b8-4bcb-9265-9d48d1fce524",
                "type": TYPE_STRING,
                "name": "given_name1",
                "lookup": "given_name1",
                "required": False,
                "label": {"English(EN)": "Given name1"},
                "hint": "",
                "choices": [],
                "associated_with": "individual",
                "xlsx_field": "given_name1_i_c",
                "scope": [Scope.GLOBAL, Scope.TARGETING, Scope.KOBO_IMPORT, Scope.INDIVIDUAL_UPDATE],
            },
            {
                "id": "36ab3421-6e7a-40d1-b816-ea5cbdcc0b6a",
                "type": TYPE_STRING,
                "name": "full_name",
                "lookup": "full_name",
                "required": True,
                "label": {"English(EN)": "Full name"},
                "hint": "",
                "choices": [],
                "associated_with": "individual",
                "xlsx_field": "full_name_i_c",
                "scope": [Scope.GLOBAL, Scope.XLSX_PEOPLE],
            },
        ],
    )
    def test_xlsx_people_scope_filtering(self) -> None:
        factory_result = FieldFactory.from_only_scopes(self.scopes)
        self.assertEqual(len(factory_result), 2)

    @patch(
        "hct_mis_api.apps.core.field_attributes.core_fields_attributes.get_core_fields_attributes",
        lambda: [
            {
                "id": "b1f90314-b8b8-4bcb-9265-9d48d1fce5a4",
                "type": TYPE_STRING,
                "name": "given_name",
                "lookup": "given_name",
                "required": False,
                "label": {"English(EN)": "Given name"},
                "hint": "",
                "choices": [],
                "associated_with": "individual",
                "xlsx_field": "given_name_i_c",
                "scope": [Scope.GLOBAL, Scope.TARGETING, Scope.KOBO_IMPORT, Scope.INDIVIDUAL_UPDATE, Scope.XLSX_PEOPLE],
            }
        ],
    )
    def test_xlsx_people_scope_modification(self) -> None:
        factory_result = FieldFactory.from_only_scopes(self.scopes)
        self.assertEqual(factory_result[0]["xlsx_field"], "pp_given_name_i_c")

    def test_get_all_core_fields_choices(self) -> None:
        choices = FieldFactory.get_all_core_fields_choices()
        self.assertEqual(len(choices), 135)
        self.assertEqual(choices[0], ("age", "Age (calculated)"))

        generate_delivery_mechanisms()
        choices = FieldFactory.get_all_core_fields_choices()
        self.assertEqual(len(choices), 148)
        self.assertEqual(
            choices[-1],
            (
                "wallet_name__transfer_to_digital_wallet",
                "Wallet Name Transfer To Digital Wallet (Transfer to Digital Wallet Delivery Mechanism)",
            ),
        )
