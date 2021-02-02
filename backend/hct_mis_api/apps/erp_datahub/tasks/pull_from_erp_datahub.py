from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.erp_datahub.models import FundsCommitment


class PullFromErpDatahubTask:
    def execute(self):
        self.update_cash_plans()
        self.update_payment_records()

    def update_cash_plans(self):
        cash_plans_without_exchange_rate = CashPlan.objects.filter(exchange_rate__isnull=True)

        for cash_plan in cash_plans_without_exchange_rate:
            try:
                funds_commitment = FundsCommitment.objects.get(funds_commitment_number=cash_plan.funds_commitment)
                cash_plan.exchange_rate = (
                    funds_commitment.total_open_amount_usd / funds_commitment.total_open_amount_local
                )
            except Exception:
                pass
        CashPlan.objects.bulk_update(cash_plans_without_exchange_rate, ["exchange_rate"])

    def update_payment_records(self):
        payment_records_to_update = PaymentRecord.objects.filter(
            delivered_quantity_usd__isnull=True, cash_plan__isnull=False, cash_plan__exchange_rate__isnull=False
        )
        for payment_record in payment_records_to_update:
            exchange_rate = payment_record.cash_plan.exchange_rate
            payment_record.delivered_quantity_usd = payment_record.delivered_quantity * exchange_rate
        PaymentRecord.objects.bulk_update(payment_records_to_update, ["delivered_quantity_usd"])
