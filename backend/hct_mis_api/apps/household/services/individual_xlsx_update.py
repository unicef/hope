from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.models import modelform_factory

import openpyxl

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
    _HOUSEHOLD,
    _INDIVIDUAL,
    FieldFactory,
    Scope,
)
from hct_mis_api.apps.household.models import Individual


class InvalidColumnsError(Exception):
    pass


class IndividualXlsxUpdate:
    DATA_ROW_INDEX = 2
    STATUS_UNIQUE = "UNIQUE"
    STATUS_NO_MATCH = "NO_MATCH"
    STATUS_MULTIPLE_MATCH = "MULTIPLE_MATCH"

    def __init__(self, xlsx_update_file):
        our_attributes = FieldFactory.from_scopes([Scope.GLOBAL, Scope.INDIVIDUAL_XLSX_UPDATE])
        self.xlsx_update_file = xlsx_update_file
        self.core_attr_by_names = {self._column_name_by_attr(attr): attr for attr in our_attributes}
        self.updatable_core_columns_names = [
            self._column_name_by_attr(attr)
            for attr in FieldFactory.from_scope(Scope.GLOBAL).associated_with_individual()
        ]
        self.xlsx_match_columns = xlsx_update_file.xlsx_match_columns or []
        self.wb = openpyxl.load_workbook(xlsx_update_file.file, data_only=True)
        self.individuals_ws = self.wb["Individuals"]
        self.report_dict = None
        self._validate_columns_names()
        self._build_helpers()

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

    def update_individuals(self):
        self.get_matching_report()

        individuals = []

        for individuals_unique_report in self.report_dict[IndividualXlsxUpdate.STATUS_UNIQUE]:
            row_num, individual = individuals_unique_report
            row = self.individuals_ws[row_num]
            individual.row_id = row_num
            individuals.append(self._update_single_individual(row, individual))

        columns = [column.replace("individual__", "") for column in self.columns_names]
        columns.append("row_id")
        Individual.objects.bulk_update(individuals, columns)

    @staticmethod
    def _column_name_by_attr(attr):
        if attr.get("associated_with") == _INDIVIDUAL:
            return f"individual__{attr.get('name')}"
        if attr.get("associated_with") == _HOUSEHOLD:
            return f"household__{attr.get('name')}"

    def _validate_columns_names(self):
        first_row = self.individuals_ws[1]

        invalid_columns = [cell.value for cell in first_row if cell.value not in self.core_attr_by_names]

        if invalid_columns:
            raise InvalidColumnsError(f"Invalid columns: {invalid_columns}")

    def _build_helpers(self):
        first_row = self.individuals_ws[1]
        self.columns_names = [cell.value for cell in first_row]
        self.columns_names_index_dict = {cell.value: cell.col_idx for cell in first_row}
        self.attr_by_column_index = {cell.col_idx: self.core_attr_by_names[cell.value] for cell in first_row}
        self.columns_match_indexes = [self.columns_names_index_dict[col] for col in self.xlsx_match_columns]
        return self.columns_names

    def _get_queryset(self):
        queryset = Individual.objects.filter(business_area=self.xlsx_update_file.business_area)

        if self.xlsx_update_file.rdi:
            queryset = queryset.filter(registration_data_import=self.xlsx_update_file.rdi)

        return queryset

    def _row_report_data(self, row):
        return row[0].row

    def _get_matching_report_for_single_row(self, row):
        q_object = Q()
        for match_col in self.xlsx_match_columns:
            attr = self.core_attr_by_names[match_col]
            value = row[self.columns_names_index_dict[match_col] - 1].value
            q_object &= Q(**{attr.get("lookup"): value})

        individuals = list(self._get_queryset().filter(q_object))
        if not individuals:
            return IndividualXlsxUpdate.STATUS_NO_MATCH, self._row_report_data(row)
        if len(individuals) > 1:
            return IndividualXlsxUpdate.STATUS_MULTIPLE_MATCH, (self._row_report_data(row), individuals)
        return IndividualXlsxUpdate.STATUS_UNIQUE, (self._row_report_data(row), individuals[0])

    def _update_single_individual(self, row, individual):
        old_individual = copy_model_object(individual)

        updated = {}
        for cell in row:
            if cell.col_idx in self.columns_match_indexes:
                continue
            name = self.attr_by_column_index[cell.col_idx]["name"]
            updated[name] = cell.value

        IndividualForm = modelform_factory(Individual, fields=updated.keys())
        form = IndividualForm(instance=individual, data=updated)

        for field in form.fields.values():
            field.required = False

        if not form.is_valid():
            raise ValidationError(form.errors)

        log_create(Individual.ACTIVITY_LOG_MAPPING, "business_area", None, old_individual, individual)

        return individual
