import openpyxl
from django.core.files import File
from openpyxl.utils import get_column_letter

# from openpyxl.worksheet.datavalidation import DataValidation
from tempfile import NamedTemporaryFile
from reporting.models import Report
from household.models import Individual


class GenerateReportService:
    HEADERS = {
        Report.INDIVIDUALS: (
            "admin_area_id",
            "business_area_id",
            "country",
            "document_id",  # 8e8ea94a-2ca5-4b76-b055-e098bc24eee8
            "household_country_origin",  # TM
            "birth_date",  # 2000-06-24
            "comms_disability",
            "deduplication_batch_results",  # {"duplicates": [], "possible_duplicates": []}
            "deduplication_golden_record_results",  # {"duplicates": [], "possible_duplicates": []}
            "deduplication_golden_record_status",  # UNIQUE_IN_BATCH
            "disability",
            "estimated_birth_date",  # False
            "hearing_disability",
            "marital_status",  # MARRIED
            "memory_disability",
            "observed_disability",  # NONE
            "physical_disability",
            "pregnant",  # False
            "relationship",
            "sanction_list_possible_match",  # False
            "seeing_disability",
            "selfcare_disability",
            "sex",  # MALE
            "work_status",  # NOT_PROVIDED
            "role_in_household",  # PRIMARY
        ),
        Report.HOUSEHOLD_DEMOGRAPHICS: (
            "admin_area_id",
            "business_area_id",
            "country",
            "unicef_id",  # HH-20-0000.0368
            "country_origin",  # TM
            "female_adults_count",  # 0
            "female_adults_disabled_count",  # 0
            "female_age_group_0_5_count",  # 0
            "female_age_group_0_5_disabled_count",  # 0
            "female_age_group_12_17_count",  # 0
            "female_age_group_12_17_disabled_count",  # 0
            "female_age_group_6_11_count",  # 0
            "female_age_group_6_11_disabled_count",  # 0
            "first_registration_date",  # 2020-08-25
            "geopoint",
            "last_registration_date",  # 2020-08-25
            "male_adults_count",  # 0
            "male_adults_disabled_count",  # 0
            "male_age_group_0_5_count",  # 0
            "male_age_group_0_5_disabled_count",  # 0
            "male_age_group_12_17_count",  # 0
            "male_age_group_12_17_disabled_count",  # 0
            "male_age_group_6_11_count",  # 0
            "male_age_group_6_11_disabed_count",  # 0
            "org_name_enumerator",
            "pregnant_count",
            "residence_status",  # HOST
            "returnee",  # False
            "size",  # 4
            "status",  # ACTIVE
            "village",
            "program_id",
        ),
        Report.CASH_PLAN_VERIFICATION: (
            "program_name",  # ?
            "activation_date",
            "cash_plan_id",
            "completion_date",
            "not_received_count",
            "received_count",
            "received_with_problems_count",
            "responded_count",
            "sample_size",
            "sampling",
            "sex_filter",
            "status",
            "verification_method",
        ),
        Report.PAYMENTS: (
            "business_area_id",
            "ca_hash_id",
            "ca_id",
            "currency",
            "delivered_quantity",
            "delivery_date",
            "delivery_type",
            "distribution_modality",
            "entitlement_quantity",
            "status",
            "target_population_cash_assist_id",
            "admin_area",
            "cash_plan_id",
            "cash_or_voucher",
        ),
        Report.PAYMENT_VERIFICATION: (
            "business_area_id",
            "cash_plan_payment_verification_id",
            "payment_record_id",
            "received_amount",
            "status",
            "status_date",
        ),
        Report.CASH_PLAN: (
            "assistance_measurement",
            "assistance_through",
            "business_area_id",
            "ca_hash_id",
            "delivery_type",
            "dispersion_date",
            "down_payment",
            "end_date",
            "funds_commitment",
            "name",
            "program_id",
            "start_date",
            "status",
            "status_date",
            "total_delivered_quantity",
            "total_entitled_quantity",
            "total_entitled_quantity_revised",
            "total_persons_covered",
            "total_persons_covered_revised",
            "total_undelivered_quantity",
            "validation_alerts_count",
            "verification_status",
            "vision_id",  # 54
        ),
        Report.PROGRAM: (
            "business_area_id",
            "administrative_areas_of_implementation",  # Test
            "budget",  # 10000.00
            "cash_plus",  # False
            "description",  # Description goes here
            "end_date",  # 2020-11-17
            "frequency_of_payments",  # REGULAR
            "id",  # e46064c4-d5e2-4990-bb9b-f5cc2dde96f9
            "name",  # Programme 13/10/2020 04:43:28
            "population_goal",  # 50
            "scope",  # UNICEF
            "sector",  # EDUCATION
            "start_date",  # 2020-10-13
            "status",  # ACTIVE
            "total_number_of_households",  # Payment records with delivered amount  > 0 to distinct households
        ),
        Report.INDIVIDUALS_AND_PAYMENT: (
            "admin_area_id",
            "business_area_id",
            "country",
            "program_name",
            "household_unicef_id",  # HH-20-0000.0368
            "household_country_origin",  # TM
            "birth_date",  # 2000-06-24
            "comms_disability",
            "deduplication_batch_results",  # {"duplicates": [], "possible_duplicates": []}
            "deduplication_golden_record_results",  # {"duplicates": [], "possible_duplicates": []}
            "deduplication_golden_record_status",  # UNIQUE
            "disability",
            "estimated_birth_date",  # False
            "hearing_disability",
            "marital_status",
            "memory_disability",
            "observed_disability",  # NONE
            "physical_disability",
            "pregnant",  # False
            "relationship",  # NON_BENEFICIARY
            "sanction_list_possible_match",  # False
            "seeing_disability",
            "selfcare_disability",
            "sex",  # Retrieving data. Wait a few seconds and try to cut or copy again.
            "work_status",  # NOT_PROVIDED
            "role",  # PRIMARY
            "currency",
            "delivered_quantity",  # Sum
            "delivered_quantity_usd",
        ),
    }
    FILTERS_SHEET = "Filters"
    TRUE_FALSE_MAPPING = {True: "YES", False: "NO"}
    MAX_COL_WIDTH = 50

    def __init__(self, report):
        self.report = report
        self.report_type = report.report_type
        self.business_area = report.business_area
        self.filter_vars = {"created_at__gte": report.date_from, "created_at__lte": report.date_to}

    def _report_type_to_str(self):
        return [name for value, name in Report.REPORT_TYPES if value == self.report_type][0]

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_report = wb.active
        ws_report.title = f"{self._report_type_to_str()} Report"
        self.wb = wb
        self.ws_report = ws_report
        self.ws_filters = wb.create_sheet(GenerateReportService.FILTERS_SHEET)
        return wb

    def _add_filters_info(self):
        filter_rows = [
            ("timeframe", f"{str(self.report.date_from)} - {str(self.report.date_to)}"),
            ("business_area", self.business_area.slug),
        ]

        if self.report.country:
            filter_rows.append(("country", str(self.report.country)))
        if self.report.admin_area:
            filter_rows.append(("admin_area", self.report.admin_area.title))
        if self.report.program:
            filter_rows.append(("program", self.program.name))

        for filter_row in filter_rows:
            self.ws_filters.append(filter_row)

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
            str(individual.admin_area.id if individual.household else ""),
            str(individual.business_area.id),
            str(individual.household.country if individual.household else ""),
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
        self.filter_vars["business_area"] = self.business_area
        if self.report.country:
            self.filter_vars["household__country"] = self.report.country
        if self.report.admin_area:
            self.filter_vars["household__admin_area"] = self.report.admin_area
        individuals = Individual.objects.filter(**self.filter_vars)

        for individual in individuals:
            self._add_individual_row(individual)

    # def _add_data_validation(self):
    #     self.dv_received = DataValidation(type="list", formula1=f'"YES,NO"', allow_blank=False)
    #     self.dv_received.add(f"B2:B{len(self.ws_verifications['B'])}")
    #     self.ws_verifications.add_data_validation(self.dv_received)
    #     cell_range = self.ws_verifications["B2":f"B{len(self.ws_verifications['B'])}"]

    def generate_workbook(self):
        self._create_workbook()
        self._add_filters_info()
        self._add_headers()
        self._add_rows()
        self._adjust_column_width_from_col(self.ws_filters, 1, 2, 1)
        self._adjust_column_width_from_col(self.ws_report, 1, len(GenerateReportService.HEADERS[self.report_type]), 0)
        return self.wb

    def generate_file(self):
        try:
            self.generate_workbook()
            with NamedTemporaryFile() as tmp:
                self.wb.save(tmp.name)
                tmp.seek(0)
                self.report.file.save(
                    f"Report:_{self._report_type_to_str()}_{str(self.report.created_at)}.xlsx", File(tmp)
                )
                self.report.status = Report.COMPLETED
        except Exception:
            self.report.status = Report.FAILED
        self.report.save()

    def _adjust_column_width_from_col(self, ws, min_col, max_col, min_row):

        column_widths = []

        for i, col in enumerate(ws.iter_cols(min_col=min_col, max_col=max_col, min_row=min_row)):

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
            ws.column_dimensions[col_name].width = value
