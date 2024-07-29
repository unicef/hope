from decimal import Decimal
from typing import Any

from django.db.models import DecimalField, Q, QuerySet
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce

from django_filters import rest_framework as filters

from hct_mis_api.apps.core.filters import DecimalRangeFilter
from hct_mis_api.apps.core.utils import decode_id_string_required
from hct_mis_api.apps.program.models import ProgramCycle


class ProgramCycleFilter(filters.FilterSet):
    search = filters.CharFilter(method="search_filter")
    status = filters.MultipleChoiceFilter(
        choices=ProgramCycle.STATUS_CHOICE,
    )
    program = filters.CharFilter(method="filter_by_program")
    total_delivered_quantity_usd = DecimalRangeFilter(method="filter_total_delivered_quantity_usd")

    class Meta:
        model = ProgramCycle
        fields = {
            "title": [
                "startswith",
            ],
            "start_date": ["gte"],
            "end_date": ["lte"],
        }

    def filter_by_program(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs.filter(program_id=decode_id_string_required(value))

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(Q(title__istartswith=value) | Q(unicef_id__istartswith=value))
        return qs.filter(q_obj)

    def filter_total_delivered_quantity_usd(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        if value:
            # annotate total_delivered_quantity_usd
            queryset = queryset.annotate(
                total_delivered_quantity_usd=Coalesce(
                    Sum("payment_plans__total_delivered_quantity_usd", output_field=DecimalField()), Decimal(0.0)
                )
            )

        return queryset.filter()
