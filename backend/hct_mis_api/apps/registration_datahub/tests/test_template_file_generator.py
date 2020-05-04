from unittest import TestCase, mock

from registration_datahub.template_generator import TemplateFileGenerator


class TestTemplateFileGenerator(TestCase):
    def test_create_workbook(self):
        wb = TemplateFileGenerator._create_workbook()

        expected_sheet_names = ["Households", "Individuals"].sort()
        result_sheet_names = wb.get_sheet_names().sort()

        self.assertEqual(expected_sheet_names, result_sheet_names)

    def test_handle_name_and_label_row(self):
        fields = {
            "test": {
                "label": {"English(EN)": "My Test Label"},
                "required": True,
                "type": "STRING",
                "choices": [],
            },
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

    @mock.patch(
        "registration_datahub.template_generator.serialize_flex_attributes",
        new=lambda: {
            "households": {
                "test_h_f": {
                    "label": {"English(EN)": "Flex Test Label"},
                    "required": False,
                    "type": "STRING",
                    "choices": [],
                }
            },
            "individuals": {
                "test_i_f": {
                    "label": {"English(EN)": "Flex Test Label 2"},
                    "required": True,
                    "type": "STRING",
                    "choices": [],
                }
            },
        },
    )
    @mock.patch.dict(
        "core.core_fields_attributes.CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY",
        {
            "households": {
                "test": {
                    "label": {"English(EN)": "My Test Label"},
                    "required": True,
                    "type": "STRING",
                    "choices": [],
                }
            },
            "individuals": {
                "test2": {
                    "label": {"English(EN)": "My Test Label 2"},
                    "required": False,
                    "type": "STRING",
                    "choices": [],
                }
            },
        },
        clear=True,
    )
    def test_add_template_columns(self):
        wb = TemplateFileGenerator._create_workbook()
        result_wb = TemplateFileGenerator._add_template_columns(wb)

        expected_households_rows = (
            ("test", "test_h_f",),
            ("My Test Label - STRING - required", "Flex Test Label - STRING",),
        )
        households_rows = tuple(
            result_wb["Households"].iter_rows(values_only=True)
        )

        self.assertEqual(expected_households_rows, households_rows)

        expected_individuals_rows = (
            ("test2", "test_i_f",),
            (
                "My Test Label 2 - STRING",
                "Flex Test Label 2 - STRING - required",
            ),
        )
        individuals_rows = tuple(
            result_wb["Individuals"].iter_rows(values_only=True)
        )

        self.assertEqual(expected_individuals_rows, individuals_rows)
