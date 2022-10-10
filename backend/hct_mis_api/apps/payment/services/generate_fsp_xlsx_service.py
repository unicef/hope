import logging
from tempfile import NamedTemporaryFile

from django.core.files import File

import openpyxl

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxReport,
)

logger = logging.getLogger(__name__)


class GenerateReportContentHelpers:
    @staticmethod
    def _to_values_list(instances, field_name: str) -> str:
        values_list = list(instances.values_list(field_name, flat=True))
        return ", ".join([str(value) for value in values_list])

    @staticmethod
    def _format_date(date) -> str:
        if not date:
            return ""
        return date.strftime("%Y-%m-%d")


class GenerateReportService:
    FILTERS_SHEET = "Meta"
    MAX_COL_WIDTH = 75

    def __init__(self, fsp: FinancialServiceProvider, business_area_slug: str = None):
        self.fsp = fsp
        self.business_area = BusinessArea.objects.get(slug=business_area_slug) if business_area_slug else None

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_report = wb.active
        ws_report.title = f"FSP {self.fsp} XLSX Report"
        self.wb = wb
        self.ws_report = ws_report
        self.ws_filters = wb.create_sheet(self.FILTERS_SHEET)
        return wb

    def _add_filters_info(self):
        self.ws_filters.append(["Business Area", self.business_area.name])

    def _add_headers(self):
        self.ws_report.append(self.fsp.fsp_xlsx_template.columns)

    def _add_rows(self) -> int:
        # TODO: fetch data from database and add rows to worksheet
        rows: list[list[str]] = []
        for row in rows:
            self.ws_report.append(row)

        return len(rows)

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()
        self._add_filters_info()
        self._add_headers()
        self._add_rows()
        # TODO: adjust column widths
        return self.wb

    def generate_report(self):
        try:
            self.generate_workbook()
            with NamedTemporaryFile() as tmp:
                self.wb.save(tmp.name)
                tmp.seek(0)
                # TODO: get payment plan id from related model
                payment_plan_id = 1000
                xlsx_file_name = (
                    f"{self.business_area.code}-{self.fsp.name}-{self.fsp.fsp_xlsx_template.id}-{payment_plan_id}.xlsx"
                )
                report = FinancialServiceProviderXlsxReport(
                    fsp=self.fsp,
                    business_area=self.business_area,
                    file=File(tmp, name=xlsx_file_name),
                )
                report.status = FinancialServiceProviderXlsxReport.COMPLETED
                report.save()
        except Exception as e:
            logger.exception(e)
