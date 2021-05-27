from decimal import Decimal

from hct_mis_api.apps.erp_datahub.models import FundsCommitment
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.models import CashPlan


def get_exchange_rate_for_cash_plan(cash_plan: CashPlan):
    if not cash_plan.funds_commitment:
        return None
    try:
        funds_commitment = FundsCommitment.objects.filter(
            funds_commitment_number=cash_plan.funds_commitment,
            total_open_amount_usd__isnull=False,
            total_open_amount_local__isnull=False,
        ).first()
        if not funds_commitment:
            return None
        return Decimal(funds_commitment.total_open_amount_usd / funds_commitment.total_open_amount_local).quantize(
            Decimal(".00000001")
        )
    except Exception:
        return None


def get_payment_record_delivered_quantity_in_usd(payment_record: PaymentRecord):
    if (
        not payment_record.delivered_quantity
        or not payment_record.cash_plan
        or not payment_record.cash_plan.exchange_rate
    ):
        return None
    if payment_record.currency == "USD":
        return payment_record.delivered_quantity
    return Decimal(payment_record.delivered_quantity * payment_record.cash_plan.exchange_rate).quantize(Decimal(".01"))
