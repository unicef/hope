from decimal import Decimal
from typing import Any

from django.db.models import DecimalField, Q, QuerySet
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce

from django_filters import rest_framework as filters

from hct_mis_api.apps.core.utils import decode_id_string_required
from hct_mis_api.apps.program.models import ProgramCycle


class ProgramCycleFilter(filters.FilterSet):
    search = filters.CharFilter(method="search_filter")
    status = filters.MultipleChoiceFilter(
        choices=ProgramCycle.STATUS_CHOICE,
    )
    program = filters.CharFilter(method="filter_by_program")
    start_date = filters.DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="end_date", lookup_expr="lte")
    title = filters.CharFilter(field_name="title", lookup_expr="istartswith")
    total_delivered_quantity_usd_from = filters.NumberFilter(method="filter_total_delivered_quantity_usd")
    total_delivered_quantity_usd_to = filters.NumberFilter(method="filter_total_delivered_quantity_usd")

    class Meta:
        model = ProgramCycle
        fields = [
            "search",
            "status",
            "program",
            "start_date",
            "end_date",
            "title",
            "total_delivered_quantity_usd_from",
            "total_delivered_quantity_usd_to",
        ]

    def filter_by_program(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs.filter(program_id=decode_id_string_required(value))

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(Q(title__istartswith=value))
        return qs.filter(q_obj)

    def filter_total_delivered_quantity_usd(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        filter_dict = {}
        filter_mapping = {
            "total_delivered_quantity_usd_from": "total_delivered_q_usd__gte",
            "total_delivered_quantity_usd_to": "total_delivered_q_usd__lte",
        }
        if value:
            queryset = queryset.annotate(
                total_delivered_q_usd=Coalesce(
                    Sum("payment_plans__total_delivered_quantity_usd", output_field=DecimalField()), Decimal(0.0)
                )
            )
            filter_dict = {filter_mapping.get(name): value}
        return queryset.filter(**filter_dict)
