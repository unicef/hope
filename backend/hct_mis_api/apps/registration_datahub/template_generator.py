from typing import List, Tuple, Dict

import openpyxl

from core.core_fields_attributes import CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY
from core.utils import serialize_flex_attributes, get_admin_areas_as_choices


class TemplateFileGenerator:
    @classmethod
    def _create_workbook(cls) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_households = wb.active
        ws_households.title = "Households"
        wb.create_sheet("Individuals")
        wb.create_sheet("Choices")

        return wb

    @classmethod
    def _handle_choices(
        cls, fields: Dict
    ) -> List[List[str]]:
        rows: List[List[str]] = [
            ["Field Name", "Label", "Value to be used in template"]
        ]

        for field_name, field_value in fields.items():
            is_admin_level = field_name in ("admin1_h_c", "admin2_h_c")
            choices = field_value["choices"]
            if is_admin_level:
                choices = get_admin_areas_as_choices(field_name[-5])
            if choices:
                for choice in field_value["choices"]:
                    row = [field_name, str(choice["label"]["English(EN)"]),
                           choice["value"]]
                    rows.append(row)

        return rows

    @classmethod
    def _handle_name_and_label_row(
        cls, fields: Dict
    ) -> Tuple[List[str], List[str]]:
        names: List[str] = []
        labels: List[str] = []

        for field_name, field_value in fields.items():
            names.append(field_name)
            label = (
                f"{field_value['label']['English(EN)']}"
                f" - {field_value['type']}"
                f"{' - required' if field_value['required'] else ''}"
            )
            labels.append(label)

        return names, labels

    @classmethod
    def _add_template_columns(cls, wb: openpyxl.Workbook) -> openpyxl.Workbook:
        households_sheet_title = "Households"
        individuals_sheet_title = "Individuals"

        ws_households = wb[households_sheet_title]
        ws_individuals = wb[individuals_sheet_title]
        ws_choices = wb["Choices"]

        flex_fields = serialize_flex_attributes()

        households_fields = {
            **CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY[
                households_sheet_title.lower()
            ],
            **flex_fields[households_sheet_title.lower()],
        }

        individuals_fields = {
            **CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY[
                individuals_sheet_title.lower()
            ],
            **flex_fields[individuals_sheet_title.lower()],
        }

        households_rows = cls._handle_name_and_label_row(households_fields)
        individuals_rows = cls._handle_name_and_label_row(individuals_fields)

        for h_row, i_row in zip(households_rows, individuals_rows):
            ws_households.append(h_row)
            ws_individuals.append(i_row)

        choices = cls._handle_choices(
            {**households_fields, **individuals_fields}
        )
        for row in choices:
            ws_choices.append(row)

        return wb

    @classmethod
    def get_template_file(cls) -> openpyxl.Workbook:
        return cls._add_template_columns(cls._create_workbook())
