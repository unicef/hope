import logging
import uuid
from datetime import datetime
from io import BytesIO
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string

import openpyxl

from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.exchange_rates.utils import (
    calculate_delivery_quantity_in_usd,
)
from hct_mis_api.apps.core.models import BusinessArea, StorageFile
from hct_mis_api.apps.core.utils import clear_cache_for_dashboard_totals
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.celery_tasks import create_cash_plan_reconciliation_xlsx
from hct_mis_api.apps.payment.models import (
    CashPlan,
    PaymentRecord,
    PaymentVerificationSummary,
)
from hct_mis_api.apps.targeting.models import TargetPopulation

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

    from hct_mis_api.apps.account.models import User

logger = logging.getLogger(__name__)

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
        reconciliation_xlsx_file: BytesIO,
        column_mapping: Dict,
        cash_plan_form_data: Dict,
        currency: str,
        delivery_type: str,
        delivery_date: str,
    ) -> None:
        self.business_area = business_area
        self.reconciliation_xlsx_file = reconciliation_xlsx_file
        self.column_mapping = column_mapping
        self.currency = currency
        self.delivery_type = delivery_type
        self.column_index_mapping = {}
        self.cash_plan_form_data = cash_plan_form_data
        self.delivery_date = delivery_date
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
        self._update_exchange_rates()
        # clear cached total numbers for dashboard statistics
        clear_cache_for_dashboard_totals()

    def _parse_header(self, header: List) -> None:
        for column, xlsx_column in self.column_mapping.items():
            if xlsx_column not in header:
                raise ValidationError(f"Column {xlsx_column} not found in the header")
            if column not in self.ALL_COLUMNS:
                raise ValidationError(f"Column {column} is not a valid column")

            self.column_index_mapping[column] = header.index(xlsx_column)

    def _parse_row(self, row: List, index: int) -> None:
        self.total_person_covered += 1
        delivered_amount = row[self.column_index_mapping[self.COLUMN_DELIVERED_AMOUNT]]
        entitlement_amount = row[self.column_index_mapping[self.COLUMN_ENTITLEMENT_QUANTITY]]
        status = (
            PaymentRecord.STATUS_SUCCESS
            if row[self.column_index_mapping[self.COLUMN_PAYMENT_STATUS]] == 1
            else PaymentRecord.STATUS_ERROR
        )
        payment_id = row[self.column_index_mapping[self.COLUMN_PAYMENT_ID]]
        target_population_id, household_id = payment_id.split(" - ")
        household = Household.objects.get(id=household_id)
        target_population = TargetPopulation.objects.get(id=target_population_id)
        currency = self.currency
        self.total_delivered_amount += delivered_amount
        self.total_entitlement_amount += entitlement_amount

        payment_record_id = self.cash_plan.ca_id + "-" + str(index + 1).zfill(7)
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
            delivery_date=self.delivery_date,
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
        new_cash_plan_index_with_padding = str(last_cash_plan_index + 1).zfill(6)
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
        PaymentVerificationSummary.objects.create(
            payment_plan_obj=self.cash_plan
        )  # previously CashPlanPaymentVerificationSummary
        self.cash_plan.save()

    def _update_exchange_rates(self) -> None:
        exchange_rates_client = ExchangeRates()
        payment_records_qs = PaymentRecord.objects.filter(cash_plan=self.cash_plan)
        for payment_record in payment_records_qs:
            calculate_delivery_quantity_in_usd(exchange_rates_client, payment_record)

        PaymentRecord.objects.bulk_update(payment_records_qs, ["delivered_quantity_usd"], 1000)

    def create_celery_task(self, user: Union["AbstractBaseUser", "AnonymousUser"]) -> None:
        reconciliation_xlsx_file = StorageFile.objects.create(
            created_by=user,
            business_area=self.business_area,
            file=self.reconciliation_xlsx_file,
        )
        program_id = self.cash_plan_form_data.pop("program").pk
        service_provider_id = self.cash_plan_form_data.pop("service_provider").pk

        create_cash_plan_reconciliation_xlsx.delay(
            str(reconciliation_xlsx_file.pk),
            self.column_mapping,
            self.cash_plan_form_data,
            self.currency,
            self.delivery_type,
            str(self.delivery_date),
            str(program_id),
            str(service_provider_id),
        )

    def send_email(self, user: "User", file_name: str, error_msg: Optional[str] = None) -> None:
        msg = "Celery task Importing Payment Records finished."

        if error_msg:
            msg = msg + f"\n{error_msg}"
        else:
            msg = msg + f"\nCashPlan ID: {self.cash_plan.ca_id}. File name: {file_name}"

        context = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "message": msg,
        }
        text_body = render_to_string("admin/payment/payment_record/import_payment_records_email.txt", context=context)
        html_body = render_to_string("admin/payment/payment_record/import_payment_records_email.html", context=context)

        email = EmailMultiAlternatives(
            subject="Importing Payment Records finished",
            from_email=settings.EMAIL_HOST_USER,
            to=[context["email"]],
            body=text_body,
        )
        email.attach_alternative(html_body, "text/html")
        result = email.send()
        if not result:
            logger.error(f"Email couldn't be send to {context['email']}")
