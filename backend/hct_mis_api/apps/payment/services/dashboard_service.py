from typing import List, Optional, TypedDict

from django.db.models import Count, Q

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentRecord, PaymentVerification
from hct_mis_api.apps.payment.utils import get_payment_items_sequence_qs


class PaymentVerificationChartQueryResponse(TypedDict):
    labels: List[str]
    datasets: List
    number_of_records: int
    average_sample_size: float


def payment_verification_chart_query(
    year: int,
    business_area_slug: str,
    collect_type: str,
    program: Optional[str] = None,
    administrative_area: Optional[str] = None,
) -> PaymentVerificationChartQueryResponse:
    status_choices_mapping = dict(PaymentVerification.STATUS_CHOICES)

    params = Q()
    params &= Q(Q(payment__delivery_date__year=year) | Q(payment_record__delivery_date__year=year))
    params &= Q(
        Q(payment__business_area__slug=business_area_slug) | Q(payment_record__business_area__slug=business_area_slug)
    )
    params &= Q(
        Q(payment__household__collect_type=collect_type) | Q(payment_record__household__collect_type=collect_type)
    )

    if program:
        params &= Q(Q(payment__parent__program__id=program) | Q(payment_record__parent__program__id=program))

    if administrative_area:
        inner_params = Q()
        inner_params |= Q(
            Q(payment__household__admin_area__id=administrative_area)
            & Q(payment__household__admin_area__area_type__area_level=2)
        )
        inner_params |= Q(
            Q(payment_record__household__admin_area__id=administrative_area)
            & Q(payment_record__household__admin_area__area_type__area_level=2)
        )
        params &= inner_params

    payment_verifications = PaymentVerification.objects.filter(params).distinct()

    verifications_by_status = (
        payment_verifications.values("status").annotate(count=Count("status")).values_list("status", "count")
    )
    verifications_by_status_dict = dict(verifications_by_status)
    dataset: List[int] = [verifications_by_status_dict.get(status, 0) for status in status_choices_mapping.keys()]
    try:
        all_verifications = sum(dataset)
        dataset_percentage = [data / all_verifications for data in dataset]
    except ZeroDivisionError:
        dataset_percentage = [0] * len(status_choices_mapping.values())
    dataset_percentage_done = [
        {"label": status, "data": [dataset_percentage_value]}
        for (dataset_percentage_value, status) in zip(dataset_percentage, status_choices_mapping.values())
    ]

    samples_count = payment_verifications.aggregate(payments_count=Count("payment") + Count("payment_record"))[
        "payments_count"
    ]
    all_payment_records_for_created_verifications = (
        get_payment_items_sequence_qs()
        .filter(
            parent__in=payment_verifications.distinct("payment_verification_plan__payment_plan_object_id").values_list(
                "payment_verification_plan__payment_plan_object_id", flat=True
            )
        )
        .filter(status=PaymentRecord.STATUS_SUCCESS, delivered_quantity__gt=0)
        .filter(household__collect_type=collect_type)
        .count()
    )
    average_sample_size: float = (
        0.0
        if all_payment_records_for_created_verifications == 0
        else samples_count / all_payment_records_for_created_verifications
    )

    households_number = (
        Household.objects.filter(
            Q(pk__in=payment_verifications.values("payment__household"))
            | Q(pk__in=payment_verifications.values("payment_record__household"))
        )
        .distinct()
        .count()
    )

    return {
        "labels": ["Payment Verification"],
        "datasets": dataset_percentage_done,
        "number_of_records": households_number,
        "average_sample_size": average_sample_size,
    }
