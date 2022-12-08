import uuid
from datetime import datetime

import openpyxl

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import CashPlan

ValidationError = Exception

class CreateCashPlanFromReconciliationService:
    COLUMN_PAYMENT_ID = "PAYMENT_ID"
    COLUMN_PAYMENT_STATUS = "PAYMENT_STATUS"
    COLUMN_DELIVERED_AMOUNT = "DELIVERED_AMOUNT"
    COLUMN_CURRENCY = "CURRENCY"
    ALL_COLUMNS = (
        COLUMN_PAYMENT_ID,
        COLUMN_PAYMENT_STATUS,
        COLUMN_DELIVERED_AMOUNT,
        COLUMN_CURRENCY,
    )

    def __init__(self, business_area_slug, reconciliation_xlsx_file, column_mapping, cash_plan_form_data):
        self.business_area = BusinessArea.objects.get(slug=business_area_slug)
        self.reconciliation_xlsx_file = reconciliation_xlsx_file
        self.column_mapping = column_mapping
        self.column_index_mapping = {}
        self.cash_plan_form_data= cash_plan_form_data

    def parse_xlsx(self):
        wb = openpyxl.load_workbook(self.reconciliation_xlsx_file)
        ws = wb.active
        rows = ws.rows
        header = [cell.value for cell in next(rows)]
        self._parse_header(header)
        for row in rows:
            row_values = [cell.value for cell in row]
            self._parse_row(row_values)

    def _parse_header(self, header: tuple):
        for column, xlsx_column in self.column_mapping.items():
            if xlsx_column not in header:
                raise ValidationError(f"Column {column} not found in the header")
            if column not in self.ALL_COLUMNS:
                raise ValidationError(f"Column {column} is not a valid column")

            self.column_index_mapping[column] = header.index(xlsx_column)

    def _parse_row(self, row: tuple):
        pass

    def _create_cash_plan(self):
        current_year = str(datetime.now().year)[-2:]
        last_cash_plan = (
            CashPlan.objects.filter(business_area=self.business_area, ca_id__startswith=f"HOPE-{current_year}-")
            .order_by("-ca_id")
            .first()
        )
        last_cash_plan_index = int(last_cash_plan.ca_id.split("-")[-1]) if last_cash_plan else 0
        new_cash_plan_index_with_padding = str(last_cash_plan_index + 1).zfill(4)
        CashPlan.objects.create(
            **self.cash_plan_form_data,
            business_area=self.business_area,
            ca_id=f"HOPE-{current_year}-{new_cash_plan_index_with_padding}",
            ca_hash_id = uuid.uuid4(),
        )
