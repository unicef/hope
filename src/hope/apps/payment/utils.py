import datetime
import hashlib
import json
import typing
from base64 import b64decode
from decimal import Decimal
from math import ceil
from typing import TYPE_CHECKING, Any, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404

from hope.apps.core.exchange_rates import ExchangeRates
from hope.apps.core.utils import chart_create_filter_query, chart_get_filtered_qs
from hope.apps.payment.models import (
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.apps.core.exchange_rates.api import ExchangeRateClient


def get_number_of_samples(
    payment_records_sample_count: int, confidence_interval: int, margin_of_error: int | float
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

    if isinstance(received_amount, str):
        received_amount = float(received_amount.strip())

    return Decimal(f"{round(received_amount, 2):.2f}")


@typing.no_type_check
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
    year: int, business_area_slug: str, filters: dict, only_with_delivered_quantity: bool = False
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
    amount: Decimal,
    currency: str,
    exchange_rate: Decimal,
    currency_exchange_date: datetime.datetime,
    exchange_rates_client: Optional["ExchangeRateClient"] = None,
) -> Decimal | None:
    if amount is None:
        return None

    if amount == 0:
        return Decimal(0)

    if not exchange_rate and exchange_rates_client is None:
        exchange_rates_client = ExchangeRates()
        exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(currency, currency_exchange_date)

    if exchange_rate is None:
        return None

    return Decimal(amount / Decimal(exchange_rate)).quantize(Decimal(".01"))


def get_payment_plan_object(payment_plan_id: str) -> "PaymentPlan":
    node_name, obj_id = b64decode(payment_plan_id).decode().split(":")
    return get_object_or_404(PaymentPlan, pk=obj_id)


def get_payment_delivered_quantity_status_and_value(
    delivered_quantity: int | float | str | None, entitlement_quantity: Decimal
) -> tuple[str, Decimal | None]:
    """
    * Fully Delivered (entitled quantity = delivered quantity) [int, float, str]
    * Partially Delivered (entitled quantity > delivered quantity > 0) [int, float, str]
    * Not Delivered (0 = delivered quantity) [int, float, str]
    * Unsuccessful (failed at the delivery processing level) [-1.0]
    """
    delivered_quantity_decimal: Decimal = to_decimal(delivered_quantity)  # type: ignore

    if delivered_quantity_decimal is None:
        raise Exception(f"Invalid delivered quantity {delivered_quantity}")

    if delivered_quantity_decimal < 0:
        return Payment.STATUS_ERROR, None

    if delivered_quantity_decimal == 0:
        return Payment.STATUS_NOT_DISTRIBUTED, delivered_quantity_decimal

    if delivered_quantity_decimal < entitlement_quantity:
        return Payment.STATUS_DISTRIBUTION_PARTIAL, delivered_quantity_decimal

    if delivered_quantity_decimal == entitlement_quantity:
        return Payment.STATUS_DISTRIBUTION_SUCCESS, delivered_quantity_decimal

    raise Exception(f"Invalid delivered quantity {delivered_quantity}")


def generate_cache_key(data: dict[str, Any]) -> str:
    task_params_str = json.dumps(data)
    return hashlib.sha256(task_params_str.encode()).hexdigest()
