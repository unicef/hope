from base64 import b64decode
import datetime
from decimal import ROUND_HALF_UP, Decimal
import hashlib
import json
from math import ceil
from typing import TYPE_CHECKING, Any, no_type_check

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Q
from django.shortcuts import get_object_or_404

from hope.apps.activity_log.utils import create_diff
from hope.apps.core.exchange_rates import ExchangeRates
from hope.apps.core.utils import chart_create_filter_query, chart_get_filtered_qs
from hope.models import (
    LogEntry,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    User,
)

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser
    from django.db.models import QuerySet

    from hope.apps.core.exchange_rates.api import ExchangeRateClient
    from hope.models.currency import Currency

# Sentinel so bulk_log_payment_changes can tell "user not provided" from an explicit user=None.
_UNSET: Any = object()

# NOTE: the activity-log helpers below deliberately re-implement what
# hope.models.log_entry.log_create() does (build a LogEntry + attach the program M2M + diff),
# bypassing it so they can bulk-insert and skip no-op diffs without per-row queries. If log_create's
# semantics change (action detection, how programs/business_area are resolved), mirror it here too.


def log_payment_plan_change(
    payment_plan: PaymentPlan,
    old_payment_plan: PaymentPlan,
    user_id: str | None,
) -> None:
    """Create an activity log entry for a PaymentPlan change applied outside a logging view.

    Async tasks and gateway/file sync flows mutate a PaymentPlan after (or without) the
    dispatching view's ``log_create()`` snapshot, so the actual changes (status, steficon rule,
    totals, ...) would otherwise go unlogged. ``user_id`` is None for system-initiated runs
    (periodic gateway sync, rebuild).

    The diff is computed once and the entry is inserted directly (instead of via ``log_create``,
    which re-diffs): this both skips no-op rows when only unmapped fields changed -- matching the
    admin ``save_model`` guard -- and avoids a second (FK-heavy) diff pass over the PaymentPlan.

    Note: PaymentPlan.ACTIVITY_LOG_MAPPING includes FK fields (financial_service_provider,
    delivery_mechanism, ...) whose values are dereferenced here for a human-readable label, so the
    diff issues a few extra SELECTs. This is once per plan (not per payment / not an N+1 over rows);
    the readable FK labels are worth the cost on these comparatively rare plan-level log writes.
    """
    changes = create_diff(old_payment_plan, payment_plan, PaymentPlan.ACTIVITY_LOG_MAPPING)
    if not changes:
        return
    user = User.objects.filter(pk=user_id).first() if user_id else None
    log = LogEntry.objects.create(
        action=LogEntry.UPDATE,
        content_object=payment_plan,
        user=user,
        business_area=payment_plan.business_area,
        object_repr=str(payment_plan),
        changes=changes,
    )
    program = payment_plan.program
    if program is not None:
        log.programs.add(program.pk)


def _log_payment_plan_event(
    payment_plan: PaymentPlan, user: "AbstractBaseUser | AnonymousUser | None", changes: dict[str, Any]
) -> None:
    """Attach a free-form activity-log entry to a PaymentPlan (events the field-diff cannot express)."""
    log = LogEntry.objects.create(
        action=LogEntry.UPDATE,
        content_object=payment_plan,
        user=user,
        business_area=payment_plan.business_area,
        object_repr=str(payment_plan),
        changes=changes,
    )
    program = payment_plan.program
    if program is not None:
        log.programs.add(program.pk)


def log_payment_plan_approval(
    payment_plan: PaymentPlan,
    user: "AbstractBaseUser | AnonymousUser | None",
    approval_type: str,
    comment: str | None,
) -> None:
    """Record an approval-workflow event (approve/authorize/release/reject) on the PaymentPlan.

    The PaymentPlan status transition is logged separately; this adds a readable entry capturing
    WHO acted at which stage and any comment, which the field-diff log cannot express.
    """
    changes: dict[str, Any] = {"acceptance_process": {"from": None, "to": approval_type}}
    if comment:
        changes["comment"] = {"from": None, "to": comment}
    _log_payment_plan_event(payment_plan, user, changes)


def log_payment_plan_supporting_document(
    payment_plan: PaymentPlan,
    user: "AbstractBaseUser | AnonymousUser | None",
    title: str,
    *,
    created: bool,
) -> None:
    """Record upload/removal of a PaymentPlan supporting (compliance) document."""
    changes = {"supporting_document": {"from": None, "to": title} if created else {"from": title, "to": None}}
    _log_payment_plan_event(payment_plan, user, changes)


def _value_repr(value: Any) -> str | None:
    """Stringify a value the same way create_diff() does (Decimals normalized)."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return str(value.normalize())
    return str(value)


def _persist_payment_logs(logs: list[LogEntry], program_ids: list[Any]) -> None:
    """Insert N payment LogEntry rows and their program M2M links in a constant number of queries."""
    if not logs:
        return
    LogEntry.objects.bulk_create(logs, batch_size=1000)
    through = LogEntry.programs.through
    links = [
        through(logentry_id=log.pk, program_id=program_id)
        for log, program_id in zip(logs, program_ids, strict=True)
        if program_id
    ]
    if links:
        through.objects.bulk_create(links, batch_size=1000)


def bulk_log_payment_changes(
    old_new_pairs: "list[tuple[Payment | None, Payment]]",
    user_id: str | None = None,
    *,
    user: Any = _UNSET,
) -> None:
    """Activity-log per-payment changes from in-memory old/new objects in one bulk insert.

    Use for bulk paths that already hold the mutated Payment objects (entitlement/delivery/status
    updates). Snapshot the old object with copy_model_object() BEFORE mutating, then pass the pairs.
    No-op diffs are skipped so unchanged rows do not create noise.

    Pass a pre-resolved ``user`` to skip the per-call user lookup -- useful when this runs once per
    batch in a loop (e.g. the steficon engine-rule task) so the same user is not fetched repeatedly.
    """
    if user is _UNSET:
        user = User.objects.filter(pk=user_id).first() if user_id else None
    content_type = ContentType.objects.get_for_model(Payment)
    logs: list[LogEntry] = []
    program_ids: list[Any] = []
    for old, new in old_new_pairs:
        changes = create_diff(old, new, Payment.ACTIVITY_LOG_MAPPING)
        if old is not None and not changes:
            continue
        logs.append(
            LogEntry(
                content_type=content_type,
                object_id=new.pk,
                action=LogEntry.UPDATE if old is not None else LogEntry.CREATE,
                user=user,
                business_area_id=new.business_area_id,
                object_repr=str(new),
                changes=changes,
            )
        )
        program_ids.append(new.program_id)
    _persist_payment_logs(logs, program_ids)


def log_payment_change(old: "Payment | None", new: Payment, user_id: str | None) -> None:
    """Activity-log a single payment change (manual edits: mark-as-failed, revert, ...)."""
    bulk_log_payment_changes([(old, new)], user_id)


def update_payments_and_log(
    queryset: "QuerySet[Payment]",
    logged_changes: dict[str, Any],
    user_id: str | None,
    extra_update: dict[str, Any] | None = None,
) -> int:
    """Apply a bulk ``.update()`` and activity-log only the mapped fields, per payment.

    ``logged_changes`` are fields tracked in ACTIVITY_LOG_MAPPING (recorded in the diff);
    ``extra_update`` are applied to the rows but not logged (e.g. *_usd, entitlement_date).
    Old values are captured with a single ``.values()`` query, so cost is constant in query count
    regardless of how many payments are affected. Returns the number of rows updated.
    """
    # Build the column list to snapshot; FK fields are compared by their *_id attname.
    column_for_field: dict[str, str] = {}
    new_compare: dict[str, Any] = {}
    new_repr: dict[str, str | None] = {}
    for field, value in logged_changes.items():
        if isinstance(value, Model):
            column = f"{field}_id"
            new_compare[field] = value.pk
            new_repr[field] = str(value)
        else:
            column = field
            new_compare[field] = value
            new_repr[field] = _value_repr(value)
        column_for_field[field] = column

    snapshot_columns = ["id", "unicef_id", "business_area_id", "program_id", *column_for_field.values()]
    rows = list(queryset.values(*snapshot_columns))

    updated = queryset.update(**{**logged_changes, **(extra_update or {})})

    user = User.objects.filter(pk=user_id).first() if user_id else None
    content_type = ContentType.objects.get_for_model(Payment)
    logs: list[LogEntry] = []
    program_ids: list[Any] = []
    for row in rows:
        changes: dict[str, Any] = {}
        for field, column in column_for_field.items():
            old_value = row[column]
            if old_value == new_compare[field]:
                continue
            changes[field] = {"from": _value_repr(old_value), "to": new_repr[field]}
        if not changes:
            continue
        logs.append(
            LogEntry(
                content_type=content_type,
                object_id=row["id"],
                action=LogEntry.UPDATE,
                user=user,
                business_area_id=row["business_area_id"],
                object_repr=row["unicef_id"] or str(row["id"]),
                changes=changes,
            )
        )
        program_ids.append(row["program_id"])
    _persist_payment_logs(logs, program_ids)
    return updated


def get_number_of_samples(
    payment_records_sample_count: int,
    confidence_interval: int,
    margin_of_error: int | float,
) -> int:
    from statistics import NormalDist

    variable = 0.5
    # fix float division by zero
    margin_of_error = margin_of_error if margin_of_error > 0 else 0.01
    z_score = NormalDist().inv_cdf(confidence_interval + (1 - confidence_interval) / 2)
    theoretical_sample = (z_score**2) * variable * (1 - variable) / margin_of_error**2
    actual_sample = ceil(
        (payment_records_sample_count * theoretical_sample / (theoretical_sample + payment_records_sample_count)) * 1.5
    )
    return min(actual_sample, payment_records_sample_count)


def from_received_to_status(received: bool, received_amount: Decimal | float, delivered_amount: Decimal | float) -> str:
    received_amount_dec = to_decimal(received_amount)
    if received is None:
        return PaymentVerification.STATUS_PENDING
    if received:
        if received_amount_dec is None:
            return PaymentVerification.STATUS_RECEIVED
        if received_amount_dec == delivered_amount:
            return PaymentVerification.STATUS_RECEIVED
        return PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
    return PaymentVerification.STATUS_NOT_RECEIVED


def to_decimal(received_amount: Decimal | float | int | str | None) -> Decimal | None:
    if received_amount is None or str(received_amount).strip() == "":
        return None

    try:
        if isinstance(received_amount, str):
            received_amount = float(received_amount.strip())
        return Decimal(f"{round(received_amount, 2):.2f}")
    except ValueError:
        return None


@no_type_check
def from_received_yes_no_to_status(received: bool, received_amount: float, delivered_amount: float) -> str:
    received_bool = None
    if received == "YES":
        received_bool = True
    elif received == "NO":
        received_bool = False
    return from_received_to_status(received_bool, received_amount, delivered_amount)


def calculate_counts(payment_verification_plan: PaymentVerificationPlan) -> None:
    payment_verification_plan.responded_count = payment_verification_plan.payment_record_verifications.filter(
        ~Q(status=PaymentVerification.STATUS_PENDING)
    ).count()
    payment_verification_plan.received_count = payment_verification_plan.payment_record_verifications.filter(
        Q(status=PaymentVerification.STATUS_RECEIVED)
    ).count()
    payment_verification_plan.not_received_count = payment_verification_plan.payment_record_verifications.filter(
        Q(status=PaymentVerification.STATUS_NOT_RECEIVED)
    ).count()
    payment_verification_plan.received_with_problems_count = (
        payment_verification_plan.payment_record_verifications.filter(
            Q(status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES)
        ).count()
    )


def get_payment_items_for_dashboard(
    year: int,
    business_area_slug: str,
    filters: dict,
    only_with_delivered_quantity: bool = False,
) -> "QuerySet":
    additional_filters = {}
    if only_with_delivered_quantity:
        additional_filters["delivered_quantity_usd__gt"] = 0
    return chart_get_filtered_qs(
        Payment.objects.filter(excluded=False, conflicted=False),
        year,
        business_area_slug_filter={"business_area__slug": business_area_slug},
        additional_filters={
            **additional_filters,
            **chart_create_filter_query(
                filters,
                program_id_path="parent__program_cycle__program__id",
                administrative_area_path="household__admin2",
            ),
        },
        year_filter_path="delivery_date",
    )


def get_quantity_in_usd(
    amount: Decimal | None,
    currency: "Currency | None",
    exchange_rate: None | Decimal | float,
    currency_exchange_date: datetime.datetime,
    exchange_rates_client: "ExchangeRates | ExchangeRateClient | None" = None,
) -> Decimal | None:
    if amount is None:
        return None

    if amount == 0:
        return Decimal(0)

    currency_code = currency.code if currency else None

    if not exchange_rate:
        if not exchange_rates_client:
            exchange_rates_client = ExchangeRates()
        exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(currency_code, currency_exchange_date)

    if exchange_rate is None:
        return None

    return Decimal(amount / Decimal(exchange_rate)).quantize(Decimal(".01"))


def normalize_score(value: float | str | Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(value).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def get_payment_plan_object(payment_plan_id: str) -> "PaymentPlan":
    node_name, obj_id = b64decode(payment_plan_id).decode().split(":")
    return get_object_or_404(PaymentPlan, pk=obj_id)


def get_payment_delivered_quantity_status_and_value(
    delivered_quantity: int | float | str | None, entitlement_quantity: Decimal
) -> tuple[str, Decimal | None]:
    """Return status and delivered quantity.

    * Fully Delivered (entitled quantity = delivered quantity) [int, float, str]
    * Partially Delivered (entitled quantity > delivered quantity > 0) [int, float, str]
    * Not Delivered (0 = delivered quantity) [int, float, str]
    * Unsuccessful (failed at the delivery processing level) [-1.0]
    """
    delivered_quantity_decimal: Decimal = to_decimal(delivered_quantity)  # type: ignore

    if delivered_quantity_decimal is None:
        raise ValueError(f"Invalid delivered quantity {delivered_quantity}")

    if delivered_quantity_decimal < 0:
        return Payment.STATUS_ERROR, None

    if delivered_quantity_decimal == 0:
        return Payment.STATUS_NOT_DISTRIBUTED, delivered_quantity_decimal

    if delivered_quantity_decimal < entitlement_quantity:
        return Payment.STATUS_DISTRIBUTION_PARTIAL, delivered_quantity_decimal

    if delivered_quantity_decimal == entitlement_quantity:
        return Payment.STATUS_DISTRIBUTION_SUCCESS, delivered_quantity_decimal

    raise ValueError(f"Invalid delivered quantity {delivered_quantity}")


def generate_cache_key(data: dict[str, Any]) -> str:
    task_params_str = json.dumps(data)
    return hashlib.sha256(task_params_str.encode()).hexdigest()


def get_link(api_url: str) -> str:
    protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
    return f"{protocol}://{settings.FRONTEND_HOST}{api_url}"
