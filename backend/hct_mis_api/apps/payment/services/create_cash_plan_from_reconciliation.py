import uuid
from datetime import datetime
from typing import IO

from django.db import transaction

import openpyxl

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerificationSummary,
    PaymentRecord,
)
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.targeting.models import TargetPopulation

ValidationError = Exception


class CreateCashPlanReconciliationService:
    COLUMN_PAYMENT_ID = "PAYMENT_ID"
    COLUMN_PAYMENT_STATUS = "PAYMENT_STATUS"
    COLUMN_DELIVERED_AMOUNT = "DELIVERED_AMOUNT"
    COLUMN_ENTITLEMENT_QUANTITY = "ENTITLEMENT_QUANTITY"
    ALL_COLUMNS = (
        COLUMN_PAYMENT_ID,
        COLUMN_PAYMENT_STATUS,
        COLUMN_DELIVERED_AMOUNT,
        COLUMN_ENTITLEMENT_QUANTITY,
    )

    def __init__(
        self,
        business_area: BusinessArea,
        reconciliation_xlsx_file: IO,
        column_mapping: dict,
        cash_plan_form_data: dict,
        currency: str,
        delivery_type: str,
    ) -> None:
        self.business_area = business_area
        self.reconciliation_xlsx_file = reconciliation_xlsx_file
        self.column_mapping = column_mapping
        self.currency = currency
        self.delivery_type = delivery_type
        self.column_index_mapping = {}
        self.cash_plan_form_data = cash_plan_form_data
        self.total_person_covered = 0
        self.total_delivered_amount = 0
        self.total_entitlement_amount = 0

    @transaction.atomic
    def parse_xlsx(self) -> None:
        wb = openpyxl.load_workbook(self.reconciliation_xlsx_file)
        ws = wb.active
        rows = ws.rows
        next(rows)
        header = [cell.value for cell in next(rows)]
        self._parse_header(header)
        self.cash_plan = self._create_cash_plan()
        print(ws.max_row)
        for index, row in enumerate(rows):
            row_values = [cell.value for cell in row]
            if all([value is None for value in row_values]):
                break
            self._parse_row(row_values, index)
        self._add_cashplan_info()

    def _parse_header(self, header: list) -> None:
        for column, xlsx_column in self.column_mapping.items():
            if xlsx_column not in header:
                raise ValidationError(f"Column {xlsx_column} not found in the header")
            if column not in self.ALL_COLUMNS:
                raise ValidationError(f"Column {column} is not a valid column")

            self.column_index_mapping[column] = header.index(xlsx_column)

    def _parse_row(self, row: tuple, index: int) -> None:
        self.total_person_covered += 1
        delivered_amount = row[self.column_index_mapping[self.COLUMN_DELIVERED_AMOUNT]]
        entitlement_amount = row[self.column_index_mapping[self.COLUMN_ENTITLEMENT_QUANTITY]]
        status = (
            PaymentRecord.STATUS_SUCCESS
            if row[self.column_index_mapping[self.COLUMN_PAYMENT_STATUS]] == 1
            else PaymentRecord.STATUS_FAILED
        )
        payment_id = row[self.column_index_mapping[self.COLUMN_PAYMENT_ID]]
        target_population_id, household_id = payment_id.split(" - ")
        household = Household.objects.get(id=household_id)
        target_population = TargetPopulation.objects.get(id=target_population_id)
        currency = self.currency
        self.total_delivered_amount += delivered_amount
        self.total_entitlement_amount += entitlement_amount

        payment_record_id = self.cash_plan.ca_id + "-" + str(index + 1).zfill(5)
        payment_record = PaymentRecord.objects.create(
            business_area=self.business_area,
            status=status,
            ca_id=payment_record_id,
            ca_hash_id=uuid.uuid4(),
            cash_plan=self.cash_plan,
            household=household,
            head_of_household=household.primary_collector,
            full_name=household.primary_collector.full_name,
            total_persons_covered=household.size,
            target_population=target_population,
            target_population_cash_assist_id="",
            currency=currency,
            entitlement_quantity=entitlement_amount,
            delivered_quantity=delivered_amount,
            service_provider=self.cash_plan.service_provider,
            status_date=self.cash_plan.status_date,
            delivery_type=self.delivery_type,
        )
        payment_record.save()

    def _create_cash_plan(self) -> CashPlan:
        current_year = str(datetime.now().year)[-2:]
        last_cash_plan = (
            CashPlan.objects.filter(business_area=self.business_area, ca_id__startswith=f"HOPE-CSH-{current_year}-")
            .order_by("-ca_id")
            .first()
        )
        last_cash_plan_index = int(last_cash_plan.ca_id.split("-")[-1]) if last_cash_plan else 0
        new_cash_plan_index_with_padding = str(last_cash_plan_index + 1).zfill(4)
        return CashPlan.objects.create(
            **self.cash_plan_form_data,
            business_area=self.business_area,
            ca_id=f"HOPE-CSH-{current_year}-{new_cash_plan_index_with_padding}",
            ca_hash_id=uuid.uuid4(),
            total_persons_covered=0,
            total_persons_covered_revised=0,
        )

    def _add_cashplan_info(self) -> None:
        self.cash_plan.total_persons_covered = self.total_person_covered
        self.cash_plan.total_persons_covered_revised = self.total_person_covered
        self.cash_plan.total_entitled_quantity = self.total_entitlement_amount
        self.cash_plan.total_delivered_quantity = self.total_delivered_amount
        CashPlanPaymentVerificationSummary.objects.create(cash_plan=self.cash_plan)
        self.cash_plan.save()
