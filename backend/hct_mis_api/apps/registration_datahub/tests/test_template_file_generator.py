from hct_mis_api.apps.core.base_test_case import DefaultTestCase
from hct_mis_api.apps.registration_datahub.template_generator import (
    TemplateFileGenerator,
)


class TestTemplateFileGenerator(DefaultTestCase):
    def test_create_workbook(self) -> None:
        wb = TemplateFileGenerator._create_workbook()

        expected_sheet_names = ["Households", "Individuals"].sort()
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

        result = TemplateFileGenerator._handle_name_and_label_row(fields)
        expected = (
            ["test", "test_h_f"],
            ["My Test Label - STRING - required", "Flex Test Label - STRING"],
        )
        self.assertEqual(expected, result)

    def test_add_template_columns(self) -> None:
        wb = TemplateFileGenerator._create_workbook()
        result_wb = TemplateFileGenerator._add_template_columns(wb)

        households_rows = tuple(result_wb["Households"].iter_rows(values_only=True))

        self.assertEqual("residence_status_h_c", households_rows[0][0])
        self.assertEqual("Residence status - SELECT_ONE", households_rows[1][0])

        individuals_rows = tuple(result_wb["Individuals"].iter_rows(values_only=True))

        self.assertEqual("age", individuals_rows[0][0])
        self.assertEqual("Age (calculated) - INTEGER", individuals_rows[1][0])
