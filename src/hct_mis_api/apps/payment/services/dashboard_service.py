from decimal import Decimal
from typing import Dict, List, Optional, TypedDict

from django.db.models import Count, DecimalField, F, Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import Payment, PaymentVerification
from hct_mis_api.apps.payment.utils import get_payment_items_for_dashboard


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
    params &= Q(payment__delivery_date__year=year)
    params &= Q(payment__business_area__slug=business_area_slug)
    params &= Q(payment__household__collect_type=collect_type)

    if program:
        params &= Q(payment__parent__program_cycle__program__id=program)

    if administrative_area:
        inner_params = Q()
        inner_params |= Q(payment__household__admin2=administrative_area)
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

    samples_count = payment_verifications.aggregate(payments_count=Count("payment"))["payments_count"]
    all_payment_records_for_created_verifications = (
        Payment.objects.filter(excluded=False, conflicted=False)
        .filter(
            parent__in=payment_verifications.distinct("payment_verification_plan__payment_plan_id").values_list(
                "payment_verification_plan__payment_plan_id", flat=True
            )
        )
        .filter(status=Payment.STATUS_SUCCESS, delivered_quantity__gt=0)
        .filter(household__collect_type=collect_type)
        .count()
    )
    average_sample_size: float = (
        0.0
        if all_payment_records_for_created_verifications == 0
        else samples_count / all_payment_records_for_created_verifications
    )

    households_number = (
        Household.objects.filter(Q(pk__in=payment_verifications.values("payment__household"))).distinct().count()
    )

    return {
        "labels": ["Payment Verification"],
        "datasets": dataset_percentage_done,
        "number_of_records": households_number,
        "average_sample_size": average_sample_size,
    }


def total_cash_transferred_by_administrative_area_table_query(
    year: int, business_area_slug: str, filters: Dict, collect_type: str
) -> QuerySet[Area]:
    payment_items_ids = (
        get_payment_items_for_dashboard(year, business_area_slug, filters, True)
        .filter(household__collect_type=collect_type)
        .values_list("id", flat=True)
    )

    return (
        Area.objects.filter(
            household__payment__id__in=payment_items_ids,
            area_type__area_level=2,
        )
        .distinct()
        .annotate(
            total_transferred_payments=Coalesce(
                Sum("household__payment__delivered_quantity_usd", output_field=DecimalField()), Decimal(0.0)
            ),
        )
        .annotate(
            num_households=Count("household", distinct=True),
            total_transferred=F("total_transferred_payments"),
        )
    )
