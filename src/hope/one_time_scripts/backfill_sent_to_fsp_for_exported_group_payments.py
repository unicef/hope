"""Backfill SENT_TO_FSP for Payments included in historical group delivery exports.

Run from a Django shell after deploying the XLSX lifecycle changes and before
resuming Payment Plan Group reconciliation imports::

    from hope.one_time_scripts.backfill_sent_to_fsp_for_exported_group_payments import backfill

    backfill()
    backfill(dry_run=False)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from django.db import transaction
from django.utils import timezone

from hope.models import FinancialServiceProvider, Payment, PaymentPlan

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    from django.db.models import QuerySet

BATCH_SIZE = 500
INTERNAL_DATA_KEY = "sent_to_fsp_group_export_backfill_history"


class BusinessAreaBackfillSummary(TypedDict):
    id: str
    name: str
    payment_plans: int
    eligible_payments: int
    updated_payments: int


class BackfillSummary(TypedDict):
    dry_run: bool
    payment_plans: int
    eligible_payments: int
    updated_payments: int
    business_areas: list[BusinessAreaBackfillSummary]


def _eligible_payment_plans() -> QuerySet[PaymentPlan]:
    return (
        PaymentPlan.objects.filter(
            status__in=(PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED),
            is_removed=False,
            payment_plan_group__isnull=False,
            export_tag__isnull=False,
            export_file_delivery__isnull=False,
            use_payment_gateway=False,
            financial_service_provider__isnull=False,
        )
        .exclude(
            financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API
        )
        .select_related("export_file_delivery", "program_cycle")
        .order_by("business_area_id", "program_cycle__program_id", "pk")
    )


def _eligible_payments(payment_plan: PaymentPlan) -> QuerySet[Payment]:
    return (
        Payment.objects.filter(
            parent=payment_plan,
            is_removed=False,
            conflicted=False,
            excluded=False,
            has_valid_wallet=True,
            status=Payment.STATUS_PENDING,
            delivered_quantity__isnull=True,
        )
        .select_related(
            "currency",
            "delivery_type",
            "household_snapshot",
        )
        .order_by("pk")
    )


def _set_backfill_values(payment: Payment, payment_plan: PaymentPlan, changed_at: datetime) -> None:
    export_file = payment_plan.export_file_delivery
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


def backfill(*, dry_run: bool = True, batch_size: int = BATCH_SIZE) -> BackfillSummary:
    partition_rows = list(
        _eligible_payment_plans()
        .order_by()
        .values_list("business_area_id", "business_area__name", "program_cycle__program_id")
        .distinct()
        .order_by("business_area_id", "business_area__name", "program_cycle__program_id")
    )
    partitions_by_business_area: dict[UUID, list[UUID]] = {}
    business_area_summaries: dict[UUID, BusinessAreaBackfillSummary] = {}
    for business_area_id, business_area_name, program_id in partition_rows:
        partitions_by_business_area.setdefault(business_area_id, []).append(program_id)
        business_area_summaries[business_area_id] = {
            "id": str(business_area_id),
            "name": business_area_name,
            "payment_plans": 0,
            "eligible_payments": 0,
            "updated_payments": 0,
        }

    changed_at = timezone.now()
    payment_plans_count = 0
    eligible_payments = 0
    updated_payments = 0
    for business_area_id, program_ids in partitions_by_business_area.items():
        business_area_summary = business_area_summaries[business_area_id]
        for program_id in program_ids:
            payment_plans = _eligible_payment_plans().filter(
                business_area_id=business_area_id,
                program_cycle__program_id=program_id,
            )
            for payment_plan in payment_plans.iterator(chunk_size=batch_size):
                payment_queryset = _eligible_payments(payment_plan)
                payment_plan_eligible_payments = 0
                payment_plan_updated_payments = 0
                if dry_run:
                    payment_plan_eligible_payments = payment_queryset.count()
                else:
                    last_pk: UUID | None = None
                    while True:
                        with transaction.atomic():
                            batch_queryset = payment_queryset.select_for_update(of=("self",))
                            if last_pk is not None:
                                batch_queryset = batch_queryset.filter(pk__gt=last_pk)
                            payments = list(batch_queryset[:batch_size])
                            if not payments:
                                break

                            for payment in payments:
                                _set_backfill_values(payment, payment_plan, changed_at)

                            Payment.signature_manager.bulk_update_with_signature(
                                payments,
                                ("status", "status_date", "internal_data"),
                                batch_size=batch_size,
                            )
                            last_pk = payments[-1].pk
                            payment_plan_eligible_payments += len(payments)
                            payment_plan_updated_payments += len(payments)

                if payment_plan_eligible_payments == 0:
                    continue
                payment_plans_count += 1
                eligible_payments += payment_plan_eligible_payments
                updated_payments += payment_plan_updated_payments
                business_area_summary["payment_plans"] += 1
                business_area_summary["eligible_payments"] += payment_plan_eligible_payments
                business_area_summary["updated_payments"] += payment_plan_updated_payments

    summary: BackfillSummary = {
        "dry_run": dry_run,
        "payment_plans": payment_plans_count,
        "eligible_payments": eligible_payments,
        "updated_payments": updated_payments,
        "business_areas": [
            business_area_summary
            for business_area_summary in business_area_summaries.values()
            if business_area_summary["payment_plans"] > 0
        ],
    }
    print(summary)
    return summary
