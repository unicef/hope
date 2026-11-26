"""Clear reconciliation for Payment Plan PP-7050-26-00000915.

Run from a production Django shell:
    from hope.one_time_scripts.clear_pp_7050_26_00000915_reconciliation import clear_reconciliation

    clear_reconciliation()
    clear_reconciliation(dry_run=False)
"""

from collections import Counter
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.models import Payment, PaymentList

PAYMENT_LIST_ID = "d85f4dd4-5285-4efc-b178-95abe456a1bd"
EXPECTED_UNICEF_ID = "PP-7050-26-00000915"
EXPECTED_PAYMENT_LIST_STATUSES = (
    PaymentList.Status.ACCEPTED,
    PaymentList.Status.FINISHED,
    PaymentList.Status.READY_FOR_CLOSURE,
    PaymentList.Status.CLOSED,
)
RECONCILIATION_REOPEN_HISTORY_KEY = "reconciliation_reopen_history"


def _validate_payment_list(payment_list: PaymentList) -> None:
    if payment_list.unicef_id != EXPECTED_UNICEF_ID:
        raise ValueError(
            f"Expected Payment List {EXPECTED_UNICEF_ID}, got {payment_list.unicef_id} for {payment_list.id}."
        )
    if payment_list.status not in EXPECTED_PAYMENT_LIST_STATUSES:
        raise ValueError(
            f"Expected {payment_list.unicef_id} to be ACCEPTED, FINISHED, READY_FOR_CLOSURE, or CLOSED, "
            f"got {payment_list.status}."
        )
    if payment_list.is_payment_gateway:
        raise ValueError(f"Payment List {payment_list.unicef_id} uses Payment Gateway. Nothing was changed.")


def _preserve_closure_data(payment_list: PaymentList, changed_at: datetime) -> None:
    internal_data = {**(payment_list.internal_data or {})}
    existing_history = internal_data.get(RECONCILIATION_REOPEN_HISTORY_KEY, [])
    if not isinstance(existing_history, list):
        raise ValueError(f"Expected {RECONCILIATION_REOPEN_HISTORY_KEY} to be a list for {payment_list.unicef_id}.")
    internal_data[RECONCILIATION_REOPEN_HISTORY_KEY] = [
        *existing_history,
        {
            "changed_at": changed_at.isoformat(),
            "previous_status": payment_list.status,
            "previous_status_date": payment_list.status_date.isoformat(),
            "closed_by_id": str(payment_list.closed_by_id) if payment_list.closed_by_id else None,
            "closure_comment": payment_list.closure_comment,
        },
    ]
    payment_list.internal_data = internal_data
    payment_list.closed_by_id = None
    payment_list.closure_comment = None


def clear_reconciliation(*, dry_run: bool = True) -> dict[str, object]:
    with transaction.atomic():
        payment_list = PaymentList.objects.select_for_update().select_related("business_area").get(id=PAYMENT_LIST_ID)
        _validate_payment_list(payment_list)

        payments = Payment.objects.select_for_update().filter(parent=payment_list).eligible()
        payment_statuses = list(payments.values_list("status", flat=True))
        payment_count = len(payment_statuses)
        if payment_count == 0:
            raise ValueError(f"No eligible payments found for {payment_list.unicef_id}. Nothing was changed.")

        summary: dict[str, object] = {
            "dry_run": dry_run,
            "payment_list_id": str(payment_list.id),
            "unicef_id": payment_list.unicef_id,
            "business_area": payment_list.business_area.slug,
            "previous_status": payment_list.status,
            "payment_status_counts": dict(sorted(Counter(payment_statuses).items())),
            "payments_to_clear": payment_count,
            "reconciliation_import_file_id": (
                str(payment_list.reconciliation_import_file_id) if payment_list.reconciliation_import_file_id else None
            ),
            "background_action_status": payment_list.background_action_status,
        }
        print(summary)
        if dry_run:
            return summary

        changed_at = timezone.now()
        payments.update(
            status=Payment.STATUS_PENDING,
            status_date=changed_at,
            delivered_quantity=None,
            delivered_quantity_usd=None,
            delivery_date=None,
        )

        update_fields = [
            "status",
            "status_date",
            "reconciliation_import_file",
            "background_action_status",
            "updated_at",
        ]
        if payment_list.status == PaymentList.Status.CLOSED:
            _preserve_closure_data(payment_list, changed_at)
            update_fields.extend(("internal_data", "closed_by_id", "closure_comment"))
        payment_list.status = PaymentList.Status.ACCEPTED
        payment_list.status_date = changed_at
        payment_list.reconciliation_import_file = None
        payment_list.background_action_status = None
        payment_list.save(update_fields=update_fields)
        payment_list.update_money_fields()
        PaymentListService(payment_list).recalculate_signatures_in_batch()

        summary["dry_run"] = False
        summary["cleared_payments"] = payment_count
        summary["new_status"] = payment_list.status
        print(summary)
        return summary
