from django.test import TestCase

from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    create_pdu_flexible_attribute,
)
from hct_mis_api.apps.core.models import PeriodicFieldData
from hct_mis_api.apps.payment.fixtures import generate_delivery_mechanisms
from hct_mis_api.apps.program.fixtures import get_program_with_dct_type_and_name
from hct_mis_api.apps.registration_data.services.template_generator_service import (
    TemplateFileGeneratorService,
)


class TestTemplateFileGenerator(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.program = get_program_with_dct_type_and_name()
        create_pdu_flexible_attribute(
            label="PDU Flex Attribute",
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=1,
            rounds_names=["May"],
            program=cls.program,
        )

    def test_create_workbook(self) -> None:
        wb = TemplateFileGeneratorService(self.program).create_workbook()

        expected_sheet_names = ["Households", "Individuals", "Import helper", "People"].sort()
        result_sheet_names = wb.sheetnames.sort()

        self.assertEqual(expected_sheet_names, result_sheet_names)

    def test_handle_name_and_label_row(self) -> None:
        fields = {
            "test": {"label": {"English(EN)": "My Test Label"}, "required": True, "type": "STRING", "choices": []},
            "test_h_f": {
                "label": {"English(EN)": "Flex Test Label"},
                "required": False,
                "type": "STRING",
                "choices": [],
            },
        }

        result = TemplateFileGeneratorService(self.program)._handle_name_and_label_row(fields)
        expected = (
            ["test", "test_h_f"],
            ["My Test Label - STRING - required", "Flex Test Label - STRING"],
        )
        self.assertEqual(expected, result)

    def test_add_template_columns(self) -> None:
        generate_delivery_mechanisms()
        result_wb = TemplateFileGeneratorService(self.program).create_workbook()

        households_rows = tuple(result_wb["Households"].iter_rows(values_only=True))

        self.assertEqual("residence_status_h_c", households_rows[0][0])
        self.assertEqual("Residence status - SELECT_ONE", households_rows[1][0])

        individuals_rows = tuple(result_wb["Individuals"].iter_rows(values_only=True))

        self.assertIn("pdu_flex_attribute_round_1_value", individuals_rows[0])
        self.assertIn("pdu_flex_attribute_round_1_collection_date", individuals_rows[0])

        self.assertEqual("age", individuals_rows[0][0])
        self.assertEqual("Age (calculated) - INTEGER", individuals_rows[1][0])

        self.assertIn("wallet_name__transfer_to_digital_wallet_i_c", individuals_rows[0])
        self.assertIn(
            "Wallet Name Transfer To Digital Wallet (Transfer to Digital Wallet Delivery Mechanism) - STRING",
            individuals_rows[1],
        )

        people_rows = tuple(result_wb["People"].iter_rows(values_only=True))

        self.assertEqual("pp_age", people_rows[0][0])
        self.assertEqual("Age (calculated) - INTEGER", people_rows[1][0])

        self.assertEqual("pp_admin3_i_c", people_rows[0][10])
        self.assertEqual("Social Worker resides in which admin3? - SELECT_ONE", people_rows[1][10])

        self.assertEqual("pp_middle_name_i_c", people_rows[0][20])
        self.assertEqual("Middle name(s) - STRING", people_rows[1][20])

        self.assertEqual("pp_drivers_license_issuer_i_c", people_rows[0][40])
        self.assertEqual("Issuing country of driver's license - SELECT_ONE", people_rows[1][40])

        self.assertEqual("pp_village_i_c", people_rows[0][70])
        self.assertEqual("Village - STRING", people_rows[1][70])

        self.assertEqual("pp_bank_branch_name_i_c", people_rows[0][86])

        self.assertEqual("pp_index_id", people_rows[0][84])
        self.assertEqual("Index ID - INTEGER - required", people_rows[1][84])

        self.assertIn("pp_wallet_name__transfer_to_digital_wallet_i_c", people_rows[0])
        self.assertIn(
            "Wallet Name Transfer To Digital Wallet (Transfer to Digital Wallet Delivery Mechanism) - STRING",
            people_rows[1],
        )
