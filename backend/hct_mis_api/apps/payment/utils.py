import datetime
import typing
from base64 import b64decode
from decimal import Decimal
from math import ceil
from typing import TYPE_CHECKING, Dict, Optional, Union

from django.db.models import Q
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.core.utils import chart_create_filter_query, chart_get_filtered_qs
from hct_mis_api.apps.payment.models import (
    CashPlan,
    Payment,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hct_mis_api.apps.core.exchange_rates.api import ExchangeRateClient


def get_number_of_samples(payment_records_sample_count: int, confidence_interval: int, margin_of_error: int) -> int:
    from statistics import NormalDist

    variable = 0.5
    z_score = NormalDist().inv_cdf(confidence_interval + (1 - confidence_interval) / 2)
    theoretical_sample = (z_score**2) * variable * (1 - variable) / margin_of_error**2
    actual_sample = ceil(
        (payment_records_sample_count * theoretical_sample / (theoretical_sample + payment_records_sample_count)) * 1.5
    )
    return min(actual_sample, payment_records_sample_count)


def from_received_to_status(
    received: bool, received_amount: Union[Decimal, float], delivered_amount: Union[Decimal, float]
) -> str:
    received_amount_dec = to_decimal(received_amount)
    if received is None:
        return PaymentVerification.STATUS_PENDING
    if received:
        if received_amount_dec is None:
            return PaymentVerification.STATUS_RECEIVED
        elif received_amount_dec == delivered_amount:
            return PaymentVerification.STATUS_RECEIVED
        else:
            return PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
    else:
        return PaymentVerification.STATUS_NOT_RECEIVED


def to_decimal(received_amount: Optional[Union[Decimal, float, int]]) -> Optional[Decimal]:
    if received_amount is None:
        return None

    if isinstance(received_amount, Decimal):
        return received_amount

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
    year: int, business_area_slug: str, filters: Dict, only_with_delivered_quantity: bool = False
) -> "QuerySet":
    additional_filters = {}
    if only_with_delivered_quantity:
        additional_filters["delivered_quantity_usd__gt"] = 0
    return chart_get_filtered_qs(
        get_payment_items_sequence_qs(),
        year,
        business_area_slug_filter={"business_area__slug": business_area_slug},
        additional_filters={
            **additional_filters,
            **chart_create_filter_query(
                filters,
                program_id_path="parent__program__id",
                administrative_area_path="household__admin_area",
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
) -> Optional[Decimal]:
    if amount is None:
        return None

    if not exchange_rate:
        if exchange_rates_client is None:
            exchange_rates_client = ExchangeRates()

            exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(currency, currency_exchange_date)

    if exchange_rate is None:
        return None

    return Decimal(amount / Decimal(exchange_rate)).quantize(Decimal(".01"))


def get_payment_items_sequence_qs() -> ExtendedQuerySetSequence:
    return ExtendedQuerySetSequence(
        Payment.objects.filter(excluded=False, conflicted=False), PaymentRecord.objects.all()
    )


def get_payment_cash_plan_items_sequence_qs() -> ExtendedQuerySetSequence:
    return ExtendedQuerySetSequence(PaymentPlan.objects.all(), CashPlan.objects.all())


def get_payment_plan_object(cash_or_payment_plan_id: str) -> Union["PaymentPlan", "CashPlan"]:
    """
    get cash_or_payment_plan_id: "UGF5bWVudFBsYW5Ob2RlOmEz4YjA2NGJkMmJmMw=="
    return CashPlan/PaymentPlan object or raise 404
    """
    node_name, obj_id = b64decode(cash_or_payment_plan_id).decode().split(":")

    payment_plan_object: Union["CashPlan", "PaymentPlan"]
    if node_name == "CashPlanNode":
        payment_plan_object = get_object_or_404(CashPlan, pk=obj_id)
    else:
        payment_plan_object = get_object_or_404(PaymentPlan, pk=obj_id)

    return payment_plan_object
