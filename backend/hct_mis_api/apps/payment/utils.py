from decimal import Decimal
from math import ceil

from scipy.special import ndtri

from payment.models import PaymentVerification


def get_number_of_samples(payment_records_sample_count, confidence_interval, margin_of_error):
    variable = 0.5
    z_score = ndtri(confidence_interval + (1 - confidence_interval) / 2)
    theoretical_sample = (z_score ** 2) * variable * (1 - variable) / margin_of_error ** 2
    actual_sample = ceil(
        (payment_records_sample_count * theoretical_sample / (theoretical_sample + payment_records_sample_count)) * 1.5
    )
    return min(actual_sample, payment_records_sample_count)


def from_received_to_status(received, received_amount, delivered_amount):
    received_amount_dec = float_to_decimal(received_amount)
    if received is None:
        return PaymentVerification.STATUS_PENDING
    if received:
        if received_amount_dec == delivered_amount:
            return PaymentVerification.STATUS_RECEIVED
        else:
            return PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
    else:
        return PaymentVerification.STATUS_NOT_RECEIVED


def float_to_decimal(received_amount):
    if isinstance(received_amount, float):
        return Decimal("{:.2f}".format(round(received_amount, 2)))
    return received_amount


def from_received_yes_no_to_status(received, received_amount, delivered_amount):
    received_bool = None
    if received == "YES":
        received_bool = True
    elif received == "NO":
        received_bool = False
    return from_received_to_status(received_bool, received_amount, delivered_amount)
