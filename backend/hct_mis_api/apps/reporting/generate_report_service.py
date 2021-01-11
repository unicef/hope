import openpyxl
from django.core.files import File
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from tempfile import NamedTemporaryFile
from reporting.models import Report
from household.models import Individual


class GenerateReportService:
    HEADERS = {
        Report.INDIVIDUALS: (
            "document_id",  # 8e8ea94a-2ca5-4b76-b055-e098bc24eee8
            "household_country_origin",  # TM
            "birth_date",  # 2000-06-24
            "comms_disability",
            "deduplication_batch_results",  # {"duplicates": [], "possible_duplicates": []}
            "deduplication_golden_record_results",  # {"duplicates": [], "possible_duplicates": []}
            "deduplication_golden_record_status",  # UNIQUE_IN_BATCH
            "disability",
            "estimated_birth_date",
            "hearing_disability",
            "marital_status",  # MARRIED
            "memory_disability",
            "observed_disability",  # NONE
            "physical_disability",
            "pregnant",
            "relationship",
            "sanction_list_possible_match",
            "seeing_disability",
            "selfcare_disability",
            "sex",  # MALE
            "work_status",  # NOT_PROVIDED
            "role_in_household",  # PRIMARY
        )
    }
    PAYMENT_RECORD_ID_COLUMN_INDEX = 0
    PAYMENT_RECORD_ID_LETTER = "A"
    RECEIVED_COLUMN_INDEX = 2
    RECEIVED_COLUMN_LETTER = "C"
    RECEIVED_AMOUNT_COLUMN_INDEX = 7
    RECEIVED_AMOUNT_COLUMN_LETTER = "H"
    META_SHEET = "Meta"
    VERSION_CELL_NAME_COORDINATES = "A1"
    VERSION_CELL_COORDINATES = "B1"
    VERSION_CELL_NAME = "FILE_TEMPLATE_VERSION"
    VERSION = "1.2"
    TRUE_FALSE_MAPPING = {True: "YES", False: "NO"}
    MAX_COL_WIDTH = 50

    def __init__(self, report):
        self.report = report
        self.report_type = report.report_type
        self.business_area = report.business_area

    def _report_type_to_str(self):
        return [name for value, name in Report.REPORT_TYPES if value == self.report_type][0]

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_report = wb.active
        ws_report.title = f"{self._report_type_to_str()} Report"
        self.wb = wb
        self.ws_report = ws_report
        return wb

    def _add_headers(self):
        headers_row = GenerateReportService.HEADERS[self.report_type]
        self.ws_report.append(headers_row)

    def _add_rows(self):
        all_type_methods = {Report.INDIVIDUALS: self._add_individuals}
        all_type_methods[self.report_type]()

    # def _to_received_column(self, payment_record_verification):
    #     status = payment_record_verification.status
    #     if payment_record_verification.status == PaymentVerification.STATUS_PENDING:
    #         return None
    #     if status == PaymentVerification.STATUS_NOT_RECEIVED:
    #         return XlsxVerificationExportService.TRUE_FALSE_MAPPING[False]
    #     return XlsxVerificationExportService.TRUE_FALSE_MAPPING[True]

    def _to_values_list(self, instances, field_name):
        values_list = list(instances.values_list(field_name, flat=True))
        return ", ".join([str(value) for value in values_list])

    def _add_individual_row(self, individual):

        individual_row = (
            self._to_values_list(individual.documents.all(), "id"),
            str(individual.household.country_origin if individual.household else ""),
            str(individual.birth_date),
            str(individual.comms_disability),
            str(individual.deduplication_batch_results),
            str(individual.deduplication_golden_record_results),
            str(individual.deduplication_golden_record_status),
            str(individual.disability),
            str(individual.estimated_birth_date),
            str(individual.hearing_disability),
            str(individual.marital_status),
            str(individual.memory_disability),
            str(individual.observed_disability),
            str(individual.physical_disability),
            str(individual.pregnant),
            str(individual.relationship),
            str(individual.sanction_list_possible_match),
            str(individual.seeing_disability),
            str(individual.selfcare_disability),
            str(individual.sex),
            str(individual.work_status),
            self._to_values_list(individual.households_and_roles.all(), "role"),
        )
        self.ws_report.append(individual_row)

    def _add_individuals(self):
        filter_vars = {"business_area": self.business_area}
        if self.report.country:
            filter_vars["household__country"] = self.report.country
        if self.report.admin_area:
            filter_vars["household__admin_area"] = self.report.admin_area
        individuals = Individual.objects.filter(**filter_vars)

        for individual in individuals:
            self._add_individual_row(individual)

    # def _add_data_validation(self):
    #     self.dv_received = DataValidation(type="list", formula1=f'"YES,NO"', allow_blank=False)
    #     self.dv_received.add(f"B2:B{len(self.ws_verifications['B'])}")
    #     self.ws_verifications.add_data_validation(self.dv_received)
    #     cell_range = self.ws_verifications["B2":f"B{len(self.ws_verifications['B'])}"]

    def generate_workbook(self):
        self._create_workbook()
        # self._add_version()
        self._add_headers()
        self._add_rows()
        self._adjust_column_width_from_col()
        return self.wb

    def generate_file(self):
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            self.wb.save(tmp.name)
            tmp.seek(0)
            self.report.file.save(f"Report:_{self._report_type_to_str()}_{str(self.report.created_at)}.xlsx", File(tmp))

    def _adjust_column_width_from_col(self):
        min_col = 1
        max_col = len(GenerateReportService.HEADERS[self.report_type])
        min_row = 0

        column_widths = []

        for i, col in enumerate(self.ws_report.iter_cols(min_col=min_col, max_col=max_col, min_row=min_row)):

            for cell in col:
                value = cell.value
                if value is not None:

                    if isinstance(value, str) is False:
                        value = str(value)

                    try:
                        column_widths[i] = max(column_widths[i], len(value))
                    except IndexError:
                        column_widths.append(len(value))

        for i, width in enumerate(column_widths):
            col_name = get_column_letter(min_col + i)
            value = column_widths[i] + 2
            value = GenerateReportService.MAX_COL_WIDTH if value > GenerateReportService.MAX_COL_WIDTH else value
            self.ws_report.column_dimensions[col_name].width = value
