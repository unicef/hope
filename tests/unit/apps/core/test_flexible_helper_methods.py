from typing import Dict, List, Optional, Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

import xlrd
from xlrd.sheet import Cell

from hct_mis_api.apps.core.flex_fields_importer import FlexibleAttributeImporter


class TestFlexibleHelperMethods(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.importer = FlexibleAttributeImporter()
        wb = xlrd.open_workbook(filename=f"{settings.TESTS_ROOT}/apps/core/test_files/flex_init.xls")
        cls.survey_sheet = wb.sheet_by_name("survey")
        cls.choices_sheet = wb.sheet_by_name("choices")
        cls.importer._reset_model_fields_variables()

    def test_get_model_fields(self) -> None:
        args = ("attribute", "group", "choice", "Not Correct Arg")
        expected_values = (
            [
                "choices",
                "is_removed",
                "id",
                "created_at",
                "updated_at",
                "type",
                "name",
                "required",
                "program",
                "pdu_data",
                "label",
                "hint",
                "group",
                "associated_with",
            ],
            [
                "flex_attributes",
                "children",
                "id",
                "created_at",
                "updated_at",
                "is_removed",
                "name",
                "label",
                "required",
                "repeatable",
                "parent",
                "lft",
                "rght",
                "tree_id",
                "level",
            ],
            [
                "is_removed",
                "id",
                "created_at",
                "updated_at",
                "list_name",
                "name",
                "label",
                "flex_attributes",
            ],
            None,
        )
        for arg, expected_value in zip(args, expected_values):
            returned_value = self.importer._get_model_fields(arg)
            self.assertEqual(returned_value, expected_value)

    def test_assign_field_values_attribute(self) -> None:
        """
        type: integer
        name: dairy_h_f
        english label: Milk and dairy products: yoghurt, cheese
        required: false
        """

        row = self.survey_sheet.row(61)
        type_value = row[0].value
        name_value = row[1].value
        required_value = row[6].value
        label_value = row[2].value

        self.importer._assign_field_values(type_value, "type", "attribute", row, 61)
        self.importer._assign_field_values(name_value, "name", "attribute", row, 61)
        self.importer._assign_field_values(required_value, "required", "attribute", row, 61)
        self.importer._assign_field_values(label_value, "label::English(EN)", "attribute", row, 61)
        expected_fields = {
            "type": "INTEGER",
            "name": "dairy_h_f",
            "required": False,
        }

        expected_json_fields = {"label": {"English(EN)": "Milk and dairy products: yoghurt, cheese"}}

        self.assertEqual(self.importer.object_fields_to_create, expected_fields)
        self.assertEqual(self.importer.json_fields_to_create, expected_json_fields)

        self.assertRaisesMessage(
            ValidationError,
            "Row 62: English label cannot be empty",
            self.importer._assign_field_values,
            "",
            "label::English(EN)",
            "attribute",
            row,
            61,
        )
        self.assertRaisesMessage(
            ValidationError,
            "Row 62: Type is required",
            self.importer._assign_field_values,
            "",
            "type",
            "attribute",
            row,
            61,
        )
        self.assertRaisesMessage(
            ValidationError,
            "Row 62: Name is required",
            self.importer._assign_field_values,
            "",
            "name",
            "attribute",
            row,
            61,
        )

    def test_assign_field_values_group(self) -> None:
        """
        name: consent
        english label: Consent
        required: false
        """
        row = self.survey_sheet.row(4)
        name_value = row[1].value
        required_value = row[6].value
        label_value = row[2].value

        self.importer._assign_field_values(name_value, "name", "group", row, 4)
        self.importer._assign_field_values(required_value, "required", "group", row, 4)
        self.importer._assign_field_values(label_value, "label::English(EN)", "group", row, 4)
        expected_fields = {
            "name": "consent",
            "required": False,
        }

        expected_json_fields = {"label": {"English(EN)": "Consent"}}

        self.assertEqual(self.importer.object_fields_to_create, expected_fields)
        self.assertEqual(self.importer.json_fields_to_create, expected_json_fields)

        self.assertRaisesMessage(
            ValidationError,
            "Row 62: Name is required",
            self.importer._assign_field_values,
            "",
            "name",
            "group",
            row,
            61,
        )

    def test_assign_field_values_choice(self) -> None:
        """
        list_name: yes_no
        name: 1
        english label: Yes
        """
        row = self.choices_sheet.row(1)
        list_name_value = row[0].value
        name_value = row[1].value
        label_value = row[2].value

        self.importer._assign_field_values(list_name_value, "list_name", "choice", row, 1)
        self.importer._assign_field_values(name_value, "name", "choice", row, 1)
        self.importer._assign_field_values(label_value, "label::English(EN)", "choice", row, 1)
        expected_fields = {
            "list_name": "yes_no",
            "name": "1",
        }

        expected_json_fields = {"label": {"English(EN)": "Yes"}}

        self.assertEqual(self.importer.object_fields_to_create, expected_fields)
        self.assertEqual(self.importer.json_fields_to_create, expected_json_fields)

        self.assertRaisesMessage(
            ValidationError,
            "Row 2: English label cannot be empty",
            self.importer._assign_field_values,
            "",
            "label::English(EN)",
            "choice",
            row,
            1,
        )
        self.assertRaisesMessage(
            ValidationError,
            "Row 2: List Name is required",
            self.importer._assign_field_values,
            "",
            "list_name",
            "choice",
            row,
            1,
        )
        self.assertRaisesMessage(
            ValidationError,
            "Row 2: Name is required",
            self.importer._assign_field_values,
            "",
            "name",
            "choice",
            row,
            1,
        )

    def test_set_can_add_flag(self) -> None:
        cases_to_test = [
            {
                "row": [
                    Cell(
                        1,
                        "text",
                        None,
                    ),
                    Cell(
                        1,
                        "test_h_c",
                        None,
                    ),
                ],
                "expected": False,
            },
            {
                "row": [
                    Cell(
                        1,
                        "text",
                        None,
                    ),
                    Cell(
                        1,
                        "test_i_c",
                        None,
                    ),
                ],
                "expected": False,
            },
            {
                "row": [
                    Cell(
                        1,
                        "start",
                        None,
                    ),
                    Cell(
                        1,
                        "start",
                        None,
                    ),
                ],
                "expected": False,
            },
            {
                "row": [
                    Cell(
                        1,
                        "end",
                        None,
                    ),
                    Cell(
                        1,
                        "end",
                        None,
                    ),
                ],
                "expected": False,
            },
            {
                "row": [
                    Cell(
                        1,
                        "deviceid",
                        None,
                    ),
                    Cell(
                        1,
                        "deviceid",
                        None,
                    ),
                ],
                "expected": False,
            },
            {
                "row": [
                    Cell(
                        1,
                        "end_repeat",
                        None,
                    ),
                    Cell(
                        1,
                        "",
                        None,
                    ),
                ],
                "expected": False,
            },
            {
                "row": [
                    Cell(
                        1,
                        "end_group",
                        None,
                    ),
                    Cell(
                        1,
                        "",
                        None,
                    ),
                ],
                "expected": False,
            },
            {
                "row": [
                    Cell(
                        1,
                        "begin_group",
                        None,
                    ),
                    Cell(
                        1,
                        "test_group",
                        None,
                    ),
                ],
                "expected": True,
            },
        ]

        for case in cases_to_test:
            self.importer.current_group_tree = [None]
            result = self.importer._can_add_row(case["row"])
            self.assertEqual(case["expected"], result)

    def test_get_list_of_field_choices(self) -> None:
        result = self.importer._get_list_of_field_choices(self.survey_sheet)
        expected = {
            "sex",
            "severity_of_disability",
            "marital_status",
            "id_type",
            "latrine",
            "disability",
            "assistance_type",
            "sufficient_water",
            "nationality",
            "child_marital_status",
            "assistance_source",
            "school_type",
            "status_head_of_hh",
            "admin2",
            "treatment_facility",
            "water_source",
            "admin1",
            "living_situation",
            "yes_no",
            "residence_status",
        }

        self.assertEqual(result, expected)

    def test_get_field_choice_name(self) -> None:
        cases_to_test: List[Dict[str, Union[List, Optional[str]]]] = [
            {
                "row": [
                    Cell(
                        1,
                        "text",
                        None,
                    ),
                    Cell(
                        1,
                        "first_name",
                        None,
                    ),
                ],
                "expected": None,
            },
            {
                "row": [
                    Cell(
                        1,
                        "select_one test_group",
                        None,
                    ),
                    Cell(
                        1,
                        "test_group",
                        None,
                    ),
                ],
                "expected": "test_group",
            },
        ]

        for case in cases_to_test:
            result = self.importer._get_field_choice_name(case["row"])
            self.assertEqual(result, case["expected"])
