import openpyxl

from hct_mis_api.apps.core.field_attributes.fields_types import Scope
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.utils import serialize_flex_attributes
from hct_mis_api.apps.geo.models import Area


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
    def _handle_choices(cls, fields: dict) -> list[list[str]]:
        rows: list[list[str]] = [["Field Name", "Label", "Value to be used in template"]]

        for field_name, field_value in fields.items():
            is_admin_level = field_name in ("admin1_h_c", "admin2_h_c")
            choices = field_value["choices"]
            if is_admin_level:
                choices = Area.get_admin_areas_as_choices(field_name[-5])
            if choices:
                for choice in field_value["choices"]:
                    row = [
                        field_name,
                        str(choice["label"]["English(EN)"]),
                        choice["value"],
                    ]
                    rows.append(row)

        return rows

    @classmethod
    def _handle_name_and_label_row(cls, fields: dict) -> tuple[list[str], list[str]]:
        names: list[str] = []
        labels: list[str] = []

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

        fields = FieldFactory.from_scopes(
            [Scope.GLOBAL, Scope.XLSX, Scope.HOUSEHOLD_ID, Scope.COLLECTOR]
        ).apply_business_area(None)
        households_fields = {
            **fields.associated_with_household().to_dict_by("xlsx_field"),
            **flex_fields[households_sheet_title.lower()],
        }

        individuals_fields = {
            **fields.associated_with_individual().to_dict_by("xlsx_field"),
            **flex_fields[individuals_sheet_title.lower()],
        }

        households_rows = cls._handle_name_and_label_row(households_fields)
        individuals_rows = cls._handle_name_and_label_row(individuals_fields)

        for h_row, i_row in zip(households_rows, individuals_rows):
            ws_households.append(h_row)
            ws_individuals.append(i_row)

        choices = cls._handle_choices({**households_fields, **individuals_fields})
        for row in choices:
            ws_choices.append(row)

        return wb

    @classmethod
    def get_template_file(cls) -> openpyxl.Workbook:
        return cls._add_template_columns(cls._create_workbook())
