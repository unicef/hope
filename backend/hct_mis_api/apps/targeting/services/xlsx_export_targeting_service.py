from functools import cached_property

import openpyxl

from hct_mis_api.apps.core.utils import nested_getattr
from hct_mis_api.apps.household.models import Individual, Document
from hct_mis_api.apps.targeting.models import TargetPopulation


class XlsxExportTargetingService:
    INDIVIDUALS_SHEET = "Individuals"
    META_SHEET = "Meta"
    VERSION_CELL_NAME_COORDINATES = "A1"
    VERSION_CELL_COORDINATES = "B1"
    VERSION_CELL_NAME = "FILE_TEMPLATE_VERSION"
    VERSION = "1.0"
    COLUMNS_MAPPING_DICT = {"household__unicef_id": "household.unicef_id", "unicef_id": "unicef_id"}

    def __init__(self, target_population: TargetPopulation):
        self.target_population = target_population
        self.documents_columns_dict = {}
        self.current_header_column_index = 0

    @cached_property
    def households(self):
        if self.target_population.status == TargetPopulation.STATUS_DRAFT:
            return self.target_population.candidate_list
        return self.target_population.vulnerability_score_filtered_households

    @cached_property
    def individuals(self):
        return Individual.objects.filter(household__in=self.households).select_related("household")

    def generate_workbook(self):
        self._create_workbook()
        self._add_version()

    def _add_version(self):
        self.ws_meta[
            XlsxExportTargetingService.VERSION_CELL_NAME_COORDINATES
        ] = XlsxExportTargetingService.VERSION_CELL_NAME
        self.ws_meta[XlsxExportTargetingService.VERSION_CELL_COORDINATES] = XlsxExportTargetingService.VERSION

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        self.ws_individuals = wb.active
        self.ws_individuals.title = XlsxExportTargetingService.INDIVIDUALS_SHEET
        self.wb = wb
        self.ws_meta = wb.create_sheet(XlsxExportTargetingService.META_SHEET)
        return wb

    def _add_standard_columns_headers(self):
        standard_columns_names = XlsxExportTargetingService.COLUMNS_MAPPING_DICT.keys()
        self.ws_individuals.append(standard_columns_names)
        self.current_header_column_index += len(standard_columns_names)

    def _add_individual_row(self, individual: Individual):
        individual_row = {
            index: nested_getattr(individual, field_name)
            for index, field_name in enumerate(XlsxExportTargetingService.COLUMNS_MAPPING_DICT.values())
        }
        self._add_individual_documents_to_row(individual, individual_row)
        self.ws_individuals.append(individual_row)

    def _add_individual_documents_to_row(self, individual: Individual, row: dict):
        document: Document
        for document in individual.documents:
            column_index = self._add_document_column_header(document)
            row[column_index] = document.document_number

    def _add_document_column_header(self, document):
        type_string = str(document.type)
        if type_string in self.documents_columns_dict:
            return self.documents_columns_dict[type_string]
        self.documents_columns_dict[type_string] = self.current_header_column_index
        self.ws_individuals[0][self.current_header_column_index] = type_string
        old_header_column_index = self.current_header_column_index
        self.current_header_column_index += 1
        return old_header_column_index

    def _add_individuals_rows(self):
        for individual in self.individuals:
            self._add_individual_row(individual)
