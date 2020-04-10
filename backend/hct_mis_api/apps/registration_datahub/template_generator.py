from typing import List, Tuple, Dict

import openpyxl

from core.core_fields_attributes import CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY
from core.utils import serialize_flex_attributes


class TemplateFileGenerator:
    @classmethod
    def _create_workbook(cls) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_households = wb.active
        ws_households.title = "Households"
        wb.create_sheet("Individuals")

        return wb

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

        return wb

    @classmethod
    def get_template_file(cls) -> openpyxl.Workbook:
        return cls._add_template_columns(cls._create_workbook())
