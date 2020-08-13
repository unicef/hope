from math import ceil

from scipy.special import ndtri


def get_number_of_samples(
    payment_records_sample_count, confidence_interval, margin_of_error
):
    variable = 0.5
    z_score = ndtri(confidence_interval + (1 - confidence_interval) / 2)
    theoretical_sample = (
        (z_score ** 2) * variable * (1 - variable) / margin_of_error ** 2
    )
    actual_sample = ceil(
        (
            payment_records_sample_count
            * theoretical_sample
            / (theoretical_sample + payment_records_sample_count)
        )
        * 1.5
    )
    return min(actual_sample, payment_records_sample_count)
