from django.db.models import Q
from django.db.transaction import atomic

from hct_mis_api.apps.payment.models import CashPlan, PaymentRecord
from hct_mis_api.apps.payment.utils import get_quantity_in_usd


class PullFromErpDatahubTask:
    @atomic()
    def execute(self):
        self.update_cash_plans()
        self.update_payment_records()

    @staticmethod
    def update_cash_plans():
        cash_plans_without_exchange_rate = CashPlan.objects.filter(exchange_rate__isnull=True)

        for cash_plan in cash_plans_without_exchange_rate:
            cash_plan.exchange_rate = cash_plan.get_exchange_rate()

            for usd_field in CashPlan.usd_fields:
                setattr(
                    cash_plan,
                    usd_field,
                    get_quantity_in_usd(
                        amount=getattr(cash_plan, usd_field.removesuffix("_usd")),
                        currency=cash_plan.currency,
                        exchange_rate=cash_plan.exchange_rate,
                        currency_exchange_date=cash_plan.currency_exchange_date,
                    ),
                )

        CashPlan.objects.bulk_update(cash_plans_without_exchange_rate, ["exchange_rate"] + CashPlan.usd_fields)

    @staticmethod
    def update_payment_records():
        payment_records_to_update = PaymentRecord.objects.filter(
            Q(delivered_quantity_usd__isnull=True, delivered_quantity__isnull=False)
            | Q(entitlement_quantity_usd__isnull=True, entitlement_quantity__isnull=False),
            parent__isnull=False,
            parent__exchange_rate__isnull=False,
        )

        for payment_record in payment_records_to_update:
            for usd_field in PaymentRecord.usd_fields:
                if getattr(payment_record, usd_field) is None:
                    setattr(
                        payment_record,
                        usd_field,
                        get_quantity_in_usd(
                            amount=getattr(payment_record, usd_field.removesuffix("_usd")),
                            currency=payment_record.currency,
                            exchange_rate=payment_record.parent.exchange_rate,
                            currency_exchange_date=payment_record.parent.currency_exchange_date,
                        ),
                    )

        PaymentRecord.objects.bulk_update(payment_records_to_update, PaymentRecord.usd_fields)
