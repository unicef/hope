from django.db.models import Sum

from hct_mis_api.apps.payment.models import PaymentRecord


def mark_as_failed(payment_record: PaymentRecord) -> None:
    payment_record.mark_as_failed()
    payment_record.save()

    recalculate_cash_received(payment_record.household)


def recalculate_cash_received(household) -> None:
    aggregated_delivered_quantity = household.payment_records.exclude(
        status=PaymentRecord.STATUS_FORCE_FAILED
    ).aggregate(
        total_cash_received=Sum("delivered_quantity"),
        total_cash_received_usd=Sum("delivered_quantity_usd"),
    )
    household.total_cash_received = aggregated_delivered_quantity["total_cash_received"]
    household.total_cash_received_usd = aggregated_delivered_quantity["total_cash_received_usd"]
    household.save(update_fields=("total_cash_received_usd", "total_cash_received_usd"))
