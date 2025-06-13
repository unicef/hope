from typing import Any, Dict

from django.db.models import Count, DecimalField, Q, QuerySet
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce, Lower

from _decimal import Decimal
from django_filters import (
    BooleanFilter,
    CharFilter,
    DateFilter,
    FilterSet,
    MultipleChoiceFilter,
    NumberFilter,
)

from hct_mis_api.apps.core.filters import DecimalRangeFilter, IntegerRangeFilter
from hct_mis_api.apps.core.utils import (
    CustomOrderingFilter,
    get_program_id_from_headers,
)
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program, ProgramCycle


class ChartProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)

    class Meta:
        fields = ("business_area",)
        model = Program

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(first_name__startswith=value)
            q_obj |= Q(last_name__startswith=value)
            q_obj |= Q(email__startswith=value)
        return qs.filter(q_obj)


class ProgramCycleFilter(FilterSet):
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=ProgramCycle.STATUS_CHOICE)
    start_date = DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = DateFilter(field_name="end_date", lookup_expr="lte")
    total_delivered_quantity_usd_from = NumberFilter(method="total_delivered_quantity_filter")
    total_delivered_quantity_usd_to = NumberFilter(method="total_delivered_quantity_filter")

    class Meta:
        fields = (
            "search",
            "status",
            "start_date",
            "end_date",
        )
        model = ProgramCycle

    order_by = CustomOrderingFilter(
        fields=(
            Lower("title"),
            "status",
            "start_date",
            "end_date",
        )
    )

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(title__istartswith=value)
        return qs.filter(q_obj)

    def total_delivered_quantity_filter(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        filter_dict = {}
        if value:
            # annotate total_delivered_quantity_usd
            queryset = queryset.annotate(
                total_delivered_quantity=Coalesce(
                    Sum("payment_plans__total_delivered_quantity_usd", output_field=DecimalField()), Decimal(0.0)
                )
            )
            if name == "total_delivered_quantity_usd_from":
                filter_dict = {"total_delivered_quantity__gte": Decimal(value)}
            elif name == "total_delivered_quantity_usd_to":
                filter_dict = {"total_delivered_quantity__lte": Decimal(value)}

        return queryset.filter(**filter_dict)
