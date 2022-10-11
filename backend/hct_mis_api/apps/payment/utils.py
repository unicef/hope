import datetime
from decimal import Decimal
from math import ceil

from django.db.models import Q

from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.core.utils import chart_create_filter_query, chart_get_filtered_qs
from hct_mis_api.apps.payment.models import (
    CashPlan,
    Payment,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
)


def get_number_of_samples(payment_records_sample_count, confidence_interval, margin_of_error):
    from statistics import NormalDist

    variable = 0.5
    z_score = NormalDist().inv_cdf(confidence_interval + (1 - confidence_interval) / 2)
    theoretical_sample = (z_score**2) * variable * (1 - variable) / margin_of_error**2
    actual_sample = ceil(
        (payment_records_sample_count * theoretical_sample / (theoretical_sample + payment_records_sample_count)) * 1.5
    )
    return min(actual_sample, payment_records_sample_count)


def from_received_to_status(received, received_amount, delivered_amount):
    received_amount_dec = float_to_decimal(received_amount)
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


def float_to_decimal(received_amount):
    if isinstance(received_amount, float):
        return Decimal(f"{round(received_amount, 2):.2f}")
    return received_amount


def from_received_yes_no_to_status(received, received_amount, delivered_amount):
    received_bool = None
    if received == "YES":
        received_bool = True
    elif received == "NO":
        received_bool = False
    return from_received_to_status(received_bool, received_amount, delivered_amount)


def calculate_counts(cash_plan_verification):
    cash_plan_verification.responded_count = cash_plan_verification.payment_record_verifications.filter(
        ~Q(status=PaymentVerification.STATUS_PENDING)
    ).count()
    cash_plan_verification.received_count = cash_plan_verification.payment_record_verifications.filter(
        Q(status=PaymentVerification.STATUS_RECEIVED)
    ).count()
    cash_plan_verification.not_received_count = cash_plan_verification.payment_record_verifications.filter(
        Q(status=PaymentVerification.STATUS_NOT_RECEIVED)
    ).count()
    cash_plan_verification.received_with_problems_count = cash_plan_verification.payment_record_verifications.filter(
        Q(status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES)
    ).count()


def get_payment_items_for_dashboard(year, business_area_slug, filters, only_with_delivered_quantity=False):
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
    exchange_rates_client=None,
):
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
    return ExtendedQuerySetSequence(Payment.objects.filter(excluded=False), PaymentRecord.objects.all())


def get_payment_cash_plan_items_sequence_qs() -> ExtendedQuerySetSequence:
    return ExtendedQuerySetSequence(PaymentPlan.objects.all(), CashPlan.objects.all())
