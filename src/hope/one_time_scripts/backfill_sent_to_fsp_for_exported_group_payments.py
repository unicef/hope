"""Backfill SENT_TO_FSP for Payments included in historical group delivery exports.

Run from a Django shell after deploying the XLSX lifecycle changes and before
resuming Payment Plan Group reconciliation imports::

    from hope.one_time_scripts.backfill_sent_to_fsp_for_exported_group_payments import backfill

    backfill()
    backfill(dry_run=False)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from hope.models import FinancialServiceProvider, Payment, PaymentPlan

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

BATCH_SIZE = 500
INTERNAL_DATA_KEY = "sent_to_fsp_group_export_backfill_history"


def _eligible_payments() -> QuerySet[Payment]:
    return (
        Payment.objects.filter(
            parent__status__in=(PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED),
            parent__is_removed=False,
            parent__payment_plan_group__isnull=False,
            parent__export_tag__isnull=False,
            parent__export_file_delivery__isnull=False,
            parent__use_payment_gateway=False,
            is_removed=False,
            conflicted=False,
            excluded=False,
            has_valid_wallet=True,
            status=Payment.STATUS_PENDING,
            delivered_quantity__isnull=True,
        )
        .filter(
            Q(parent__financial_service_provider__isnull=True)
            | ~Q(
                parent__financial_service_provider__communication_channel=(
                    FinancialServiceProvider.COMMUNICATION_CHANNEL_API
                )
            )
        )
        .select_related("parent__export_file_delivery")
        .order_by("pk")
    )


def _set_backfill_values(payment: Payment, changed_at: datetime) -> None:
    export_file = payment.parent.export_file_delivery
    if export_file is None:
        raise ValueError(f"Payment {payment.pk} has no delivery export file.")
    previous_status_date = payment.status_date
    internal_data = {**(payment.internal_data or {})}
    history = internal_data.get(INTERNAL_DATA_KEY, [])
    if not isinstance(history, list):
        raise ValueError(f"Expected {INTERNAL_DATA_KEY} to be a list for Payment {payment.pk}.")
    payment.status = Payment.STATUS_SENT_TO_FSP
    payment.status_date = export_file.created
    internal_data[INTERNAL_DATA_KEY] = [
        *history,
        {
            "changed_at": changed_at.isoformat(),
            "export_file_id": str(export_file.pk),
            "exported_at": export_file.created.isoformat(),
            "previous_status": Payment.STATUS_PENDING,
            "previous_status_date": previous_status_date.isoformat() if previous_status_date else None,
        },
    ]
    payment.internal_data = internal_data


def backfill(*, dry_run: bool = True, batch_size: int = BATCH_SIZE) -> dict[str, int | bool]:
    queryset = _eligible_payments()
    eligible_count = queryset.count()
    summary: dict[str, int | bool] = {
        "dry_run": dry_run,
        "eligible_payments": eligible_count,
        "updated_payments": 0,
    }
    print(summary)
    if dry_run or eligible_count == 0:
        return summary

    changed_at = timezone.now()
    last_pk: UUID | None = None
    updated_payments = 0
    while True:
        with transaction.atomic():
            batch_queryset = queryset.select_for_update()
            if last_pk is not None:
                batch_queryset = batch_queryset.filter(pk__gt=last_pk)
            payments = list(batch_queryset[:batch_size])
            if not payments:
                break

            for payment in payments:
                _set_backfill_values(payment, changed_at)

            Payment.signature_manager.bulk_update_with_signature(
                payments,
                ("status", "status_date", "internal_data"),
                batch_size=batch_size,
            )
            last_pk = payments[-1].pk
            updated_payments += len(payments)

    summary["updated_payments"] = updated_payments
    print(summary)
    return summary
