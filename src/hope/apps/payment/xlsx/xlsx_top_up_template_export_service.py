from typing import TYPE_CHECKING

import openpyxl

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.models import FinancialServiceProviderXlsxTemplate, Payment, PaymentPlan

if TYPE_CHECKING:
    from django.db.models import QuerySet


class XlsxTopUpTemplateExportService(XlsxPaymentPlanBaseService, XlsxExportBaseService):
    """Generate a top-up XLSX template from the eligible beneficiaries of a Standard plan.

    The template is read by ops staff to fill in per-beneficiary top-up amounts and
    then re-uploaded through ``XlsxTopUpCreateImportService`` to create the TopUp PP.
    """

    KEY_COLUMN = "household_unicef_id"
    TITLE = "Top Up - Template"
    HEADERS = (
        KEY_COLUMN,
        "household_size",
        "admin_level_2",
        "village",
        "collector_name",
        "currency",
        "entitlement_quantity",
    )

    def __init__(self, source_payment_plan: PaymentPlan) -> None:
        self.source_payment_plan = source_payment_plan
        self.headers = list(self.HEADERS)
        self.admin_areas_dict = FinancialServiceProviderXlsxTemplate.get_areas_dict()

    def _eligible_payments(self) -> "QuerySet[Payment]":
        return self.source_payment_plan.eligible_payments_for_top_up().select_related(
            "household", "collector", "currency"
        )

    def _build_row(self, payment: Payment) -> list:
        household = payment.household
        collector_name = ""
        if payment.collector_id and payment.collector is not None:
            collector_name = payment.collector.full_name or ""
        admin_level_2 = ""
        if household.admin2_id:
            admin_level_2 = self.admin_areas_dict.get(household.admin2_id, "") or ""
        currency_code = payment.currency.code if payment.currency_id else ""
        return [
            household.unicef_id,
            household.size or "",
            admin_level_2,
            household.village or "",
            collector_name,
            currency_code,
            "",
        ]

    def _add_rows(self) -> None:
        for payment in self._eligible_payments().iterator(chunk_size=2000):
            self.ws_export_list.append(self._build_row(payment))

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()
        self._add_headers()
        self._add_rows()
        self._adjust_column_width_from_col(ws=self.ws_export_list)
        self._add_col_bgcolor([self.headers.index("entitlement_quantity") + 1])
        return self.wb

    def write_to_stream(self, stream) -> None:
        """Render the workbook to an open binary stream (used by the API response)."""
        self.generate_workbook()
        self.wb.save(stream)
