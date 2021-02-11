import openpyxl
import copy
from django.core.files import File
from openpyxl.utils import get_column_letter
from django.db.models import Min, Max, Sum, Q, Count
from django.contrib.postgres.aggregates.general import ArrayAgg
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from tempfile import NamedTemporaryFile

from hct_mis_api.apps.core.models import AdminArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.reporting.models import Report, DashboardReport
from hct_mis_api.apps.household.models import Individual, Household, ACTIVE
from hct_mis_api.apps.program.models import CashPlanPaymentVerification, CashPlan, Program
from hct_mis_api.apps.payment.models import PaymentRecord, PaymentVerification
from hct_mis_api.apps.core.utils import decode_id_string


class GenerateDashboardReportContentHelpers:
    @staticmethod
    def _to_values_list(instances, field_name: str) -> str:
        values_list = list(instances.values_list(field_name, flat=True))
        return ", ".join([str(value) for value in values_list])

    @staticmethod
    def _format_date(date) -> str:
        if not date:
            return ""
        return date.strftime("%Y-%m-%d")


class GenerateDashboardReportService:
    HQ = 1
    COUNTRY = 2
    HEADERS = {
        DashboardReport.BENEFICIARIES_REACHED: {
            HQ: ("business area", "country", "households reached", "individuals reached", "children reached"),
            COUNTRY: ("business area", "programme", "households reached", "individuals reached", "children reached"),
        }
    }
    META_HEADERS = ("report type", "creation date", "created by", "business area", "report year")
    META_SHEET = "Meta data"
    MAX_COL_WIDTH = 75

    def __init__(self, report: DashboardReport):
        self.report = report
        self.report_types = report.report_type
        self.business_area = report.business_area
        # TODO check if this is best way to determin if global
        self.hq_or_country = self.HQ if report.business_area.slug == "global" else self.COUNTRY

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_meta = wb.active
        ws_meta.title = self.META_SHEET
        self.wb = wb
        self.ws_meta = ws_meta
        return wb

    def _format_meta_tab(self):
        self.ws_meta.append(self.META_HEADERS)
        info_row = (
            self._report_types_to_joined_str(),
            self._format_date(self.report.created_at),
            self.report.created_by,
            self.business_area.name,
            str(self.report.year),
        )
        self.ws_meta.append(info_row)

    def _add_headers(self, active_sheet, report_type):
        headers_row = self.HEADERS[report_type][self.hq_or_country]
        active_sheet.append(headers_row)

    def _add_rows(self):
        pass
        # get_row_methods = GenerateReportService.ROW_CONTENT_METHODS[self.report_type]
        # all_instances = get_row_methods[0](self.report)
        # self.report.number_of_records = all_instances.count()
        # number_of_columns_based_on_set_headers = len(GenerateReportService.HEADERS[self.report_type])
        # col_instances_len = 0
        # for instance in all_instances:
        #     row = get_row_methods[1](instance)
        #     str_row = self._stringify_all_values(row)
        #     if len(str_row) > col_instances_len:
        #         col_instances_len = len(str_row)
        #     self.ws_report.append(str_row)
        # if col_instances_len > number_of_columns_based_on_set_headers:
        #     # to cover bases when we create extra columns for reverse foreign key instances and we don't know in advance how many columns there will be
        #     self._add_missing_headers(
        #         self.ws_report,
        #         number_of_columns_based_on_set_headers + 1,
        #         col_instances_len,
        #         GenerateReportService.OPTIONAL_HEADERS.get(self.report_type, ""),
        #     )
        # return col_instances_len

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()
        self._format_meta_tab()
        self._adjust_column_width_from_col(self.ws_meta, 1, 5, 1)

        # loop through all selected report types and add sheet for each
        for report_type in self.report_types:
            print("IN FOR LOOP", report_type)
            sheet_title = self._report_type_to_str(report_type)
            print("SHEET TITLE", sheet_title)
            active_sheet = self.wb.create_sheet(sheet_title)
            print("CREATED ACTIVE SHEET")
            self._add_headers(active_sheet, report_type)
            print("ADDED HEADERS")
            self._add_rows()
            print("ADDED ROWS")
            self._adjust_column_width_from_col(active_sheet, 1, len(self.HEADERS[report_type][self.hq_or_country]), 0)
            print("ADJUTED WIDTH")
        return self.wb

    def generate_report(self):
        try:
            self.generate_workbook()
            print(self.wb)
            with NamedTemporaryFile() as tmp:
                self.wb.save(tmp.name)
                tmp.seek(0)
                self.report.file.save(
                    f"{self._report_types_to_joined_str()}-{GenerateDashboardReportContentHelpers._format_date(self.report.created_at)}.xlsx",
                    File(tmp),
                    save=False,
                )
                self.report.status = DashboardReport.COMPLETED
        except Exception as e:
            print("ERROR", e)
            self.report.status = DashboardReport.FAILED
        self.report.save()

        if self.report.file:
            self._send_email()

    def _send_email(self):
        pass
        # context = {
        #     "report_type": self._report_type_to_str(),
        #     "created_at": GenerateReportContentHelpers._format_date(self.report.created_at),
        #     "report_url": f'https://{settings.FRONTEND_HOST}/{self.business_area.slug}/reporting/{encode_id_base64(self.report.id, "Report")}',
        # }
        # text_body = render_to_string("report.txt", context=context)
        # html_body = render_to_string("report.html", context=context)
        # msg = EmailMultiAlternatives(
        #     subject="HOPE report generated",
        #     from_email=settings.EMAIL_HOST_USER,
        #     to=[self.report.created_by.email],
        #     body=text_body,
        # )
        # msg.attach_alternative(html_body, "text/html")
        # msg.send()

    def _adjust_column_width_from_col(self, ws, min_col, max_col, min_row):

        column_widths = []

        for i, col in enumerate(ws.iter_cols(min_col=min_col, max_col=max_col, min_row=min_row)):

            for cell in col:
                value = cell.value

                if value is not None:

                    if isinstance(value, str) is False:
                        value = str(value)

                    if len(value) > GenerateDashboardReportService.MAX_COL_WIDTH:
                        alignment = copy.copy(cell.alignment)
                        alignment.wrapText = True
                        cell.alignment = alignment

                    try:
                        column_widths[i] = max(column_widths[i], len(value))
                    except IndexError:
                        column_widths.append(len(value))

        for i, width in enumerate(column_widths):
            col_name = get_column_letter(min_col + i)
            value = column_widths[i] + 2
            value = (
                GenerateDashboardReportService.MAX_COL_WIDTH
                if value > GenerateDashboardReportService.MAX_COL_WIDTH
                else value
            )
            ws.column_dimensions[col_name].width = value

    def _report_type_to_str(self, report_type) -> str:
        return str([name for value, name in Report.REPORT_TYPES if value == report_type][0])

    def _report_types_to_joined_str(self) -> str:
        return ", ".join([self._report_type_to_str(report_type) for report_type in self.report_types])

    def _stringify_all_values(self, row: tuple) -> tuple:
        str_row = []
        for value in row:
            str_row.append(str(value if value is not None else ""))
        return tuple(str_row)

    def _format_date(self, date) -> str:
        if not date:
            return ""
        return date.strftime("%Y-%m-%d")
