from django.db.transaction import atomic

from hct_mis_api.apps.erp_datahub.utils import (
    get_exchange_rate_for_cash_plan,
    get_payment_record_delivered_quantity_in_usd,
)
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.models import CashPlan


class PullFromErpDatahubTask:
    @atomic()
    def execute(self):
        self.update_cash_plans()
        self.update_payment_records()

    def update_cash_plans(self):
        cash_plans_without_exchange_rate = CashPlan.objects.filter(exchange_rate__isnull=True)

        for cash_plan in cash_plans_without_exchange_rate:
            cash_plan.exchange_rate = get_exchange_rate_for_cash_plan(cash_plan)

        CashPlan.objects.bulk_update(cash_plans_without_exchange_rate, ["exchange_rate"])

    def update_payment_records(self):
        payment_records_to_update = PaymentRecord.objects.filter(
            delivered_quantity_usd__isnull=True,
            delivered_quantity__isnull=False,
            cash_plan__isnull=False,
            cash_plan__exchange_rate__isnull=False,
        )
        for payment_record in payment_records_to_update:
            payment_record.delivered_quantity_usd = get_payment_record_delivered_quantity_in_usd(payment_record)

        PaymentRecord.objects.bulk_update(payment_records_to_update, ["delivered_quantity_usd"])
