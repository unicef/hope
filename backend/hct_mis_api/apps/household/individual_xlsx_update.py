import openpyxl

from hct_mis_api.apps.core.core_fields_attributes import CORE_FIELDS_ATTRIBUTES, _INDIVIDUAL


class IndividualXlsxUpdate:
    def __init__(self, xlsx_update_file):
        self.core_columns_names = [attr["xlsx_field"] for attr in CORE_FIELDS_ATTRIBUTES]
        self.updatable_core_columns_names = [
            attr["xlsx_field"] for attr in CORE_FIELDS_ATTRIBUTES if attr["associated_with"] == _INDIVIDUAL
        ]
        self.wb = openpyxl.load_workbook(xlsx_update_file.file, data_only=True)
        self.individuals_ws = self.wb["Individuals"]
        self._get_xlsx_column_names()

    def _get_xlsx_column_names(self):
        first_row = self.individuals_ws[0]
        self.columns_names = [cell.value for cell in first_row]
        return self.columns_names
