import openpyxl
from django.db.models import Q

from hct_mis_api.apps.core.core_fields_attributes import CORE_FIELDS_ATTRIBUTES, _INDIVIDUAL, _HOUSEHOLD
from hct_mis_api.apps.household.models import Individual


class IndividualXlsxUpdate:
    DATA_ROW_INDEX = 2
    STATUS_UNIQUE = "UNIQUE"
    STATUS_NO_MATCH = "NO_MATCH"
    STATUS_MULTIPLE_MATCH = "MULTIPLE_MATCH"

    def __init__(self, xlsx_update_file):
        self.xlsx_update_file = xlsx_update_file
        self.core_columns_names = [self._column_name_by_attr(attr) for attr in CORE_FIELDS_ATTRIBUTES]
        self.core_attr_by_xlsx_names = {self._column_name_by_attr(attr): attr for attr in CORE_FIELDS_ATTRIBUTES}
        self.updatable_core_columns_names = [
            self._column_name_by_attr(attr) for attr in CORE_FIELDS_ATTRIBUTES if attr["associated_with"] == _INDIVIDUAL
        ]
        self.xlsx_match_columns = xlsx_update_file.xlsx_match_columns or []
        self.wb = openpyxl.load_workbook(xlsx_update_file.file, data_only=True)
        self.individuals_ws = self.wb["Individuals"]
        self.report_dict = None
        self._get_xlsx_column_names()

    @staticmethod
    def _column_name_by_attr(attr):
        if attr.get("associated_with") == _INDIVIDUAL:
            return f"individual__{attr.get('xlsx_field')}"
        if attr.get("associated_with") == _HOUSEHOLD:
            return f"household__{attr.get('xlsx_field')}"

    def _get_xlsx_column_names(self):
        first_row = self.individuals_ws[1]
        self.columns_names = [cell.value for cell in first_row]
        self.columns_names_index_dict = {cell.value: cell.col_idx for cell in first_row}
        return self.columns_names

    def get_queryset(self):
        queryset = Individual.objects.filter(business_area=self.xlsx_update_file.business_area)
        if self.xlsx_update_file.rdi:
            queryset.filter(registration_data_import=self.xlsx_update_file.rdi)
        return queryset

    def _row_report_data(self, row):
        return row[0].row

    def _get_matching_report_for_single_row(self, row):
        q_object = Q()
        for match_col in self.xlsx_match_columns:
            attr = self.core_attr_by_xlsx_names[match_col]
            value = row[self.columns_names_index_dict[match_col] - 1].value
            q_object &= Q(**{attr.get("lookup"): value})

        import ipdb

        ipdb.set_trace()
        individuals = list(self.get_queryset().filter(q_object))
        if not individuals:
            return IndividualXlsxUpdate.STATUS_NO_MATCH, self._row_report_data(row)
        if len(individuals) > 1:
            return IndividualXlsxUpdate.STATUS_MULTIPLE_MATCH, (self._row_report_data(row), individuals)
        return IndividualXlsxUpdate.STATUS_UNIQUE, (self._row_report_data(row), individuals[0])

    def get_matching_report(self):
        report_dict = {
            IndividualXlsxUpdate.STATUS_UNIQUE: [],
            IndividualXlsxUpdate.STATUS_NO_MATCH: [],
            IndividualXlsxUpdate.STATUS_MULTIPLE_MATCH: [],
        }
        for row in self.individuals_ws.iter_rows(min_row=IndividualXlsxUpdate.DATA_ROW_INDEX):
            (status, data) = self._get_matching_report_for_single_row(row)
            report_dict[status].append(data)
        self.report_dict = report_dict
        return report_dict
