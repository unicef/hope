import uuid
from datetime import datetime

import openpyxl

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.targeting.models import TargetPopulation

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
        self.cash_plan_form_data = cash_plan_form_data

    def parse_xlsx(self):
        wb = openpyxl.load_workbook(self.reconciliation_xlsx_file)
        ws = wb.active
        rows = ws.rows
        header = [cell.value for cell in next(rows)]
        self._parse_header(header)
        self.cash_plan = self._create_cash_plan()
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

    def _parse_row(self, row: tuple,index):
        delivered_amount = row[self.column_index_mapping[self.COLUMN_DELIVERED_AMOUNT]]
        status = row[self.column_index_mapping[self.COLUMN_PAYMENT_STATUS]]
        payment_id = row[self.column_index_mapping[self.COLUMN_PAYMENT_ID]]
        target_population_id, unicef_id = payment_id.split("/")
        household = Household.objects.get(unicef_id=unicef_id)
        target_population = TargetPopulation.objects.get(id=target_population_id)
        currency = row[self.column_index_mapping[self.COLUMN_CURRENCY]]
        # delivery method
        # distribution_modality
        # target_population_cash_assist_id
        # delivery_type
        # delivery_date

        payment_record_id = self.cash_plan.ca_id + "-" + str(index+1).zfill(5)
        payment_record = PaymentRecord.objects.create(busines_area=self.business_area,
                                                      status=status,
                                                      ca_id= payment_record_id,
                                                      ca_hash_id= uuid.uuid4(),
                                                        cash_plan=self.cash_plan,
                                                      household = household,
                                                      head_of_household = household.primary_collector,
                                                      full_name= household.primary_collector.full_name,
                                                      total_persons_covered = household.size,
                                                      target_population= target_population,
                                                      target_population_cash_assist_id ='',
                                                      currency= currency,
                                                      entitlement_quantity = delivered_amount,
                                                      delivered_quantity = delivered_amount,
                                                      service_provider = self.cash_plan.service_provider,
                                                      )
        payment_record.save()





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
            ca_hash_id=uuid.uuid4(),
        )
