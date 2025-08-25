from decimal import Decimal
from typing import Any

from django.db.models import DecimalField, Q, QuerySet
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import Coalesce, Lower
from django_filters import rest_framework as filters

from hope.apps.core.api.filters import UpdatedAtFilter
from hope.apps.core.utils import CustomOrderingFilter
from hope.apps.payment.models import PaymentPlan
from models.program import Program, ProgramCycle


class ProgramCycleFilter(UpdatedAtFilter):
    search = filters.CharFilter(method="search_filter")
    status = filters.MultipleChoiceFilter(
        choices=ProgramCycle.STATUS_CHOICE,
    )
    start_date = filters.DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="end_date", lookup_expr="lte")
    title = filters.CharFilter(field_name="title", lookup_expr="istartswith")
    total_delivered_quantity_usd_from = filters.NumberFilter(method="filter_total_delivered_quantity_usd")
    total_delivered_quantity_usd_to = filters.NumberFilter(method="filter_total_delivered_quantity_usd")
    total_entitled_quantity_usd_from = filters.NumberFilter(method="filter_total_entitled_quantity_usd")
    total_entitled_quantity_usd_to = filters.NumberFilter(method="filter_total_entitled_quantity_usd")

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

    def search_filter(self, qs: QuerySet, name: str, values: Any) -> QuerySet:
        q_obj = Q()
        for value in values.split(" "):
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
                    Sum(
                        "payment_plans__total_delivered_quantity_usd",
                        output_field=DecimalField(),
                    ),
                    Decimal(0.0),
                )
            )
            filter_dict = {filter_mapping.get(name): value}
        return queryset.filter(**filter_dict)

    def filter_total_entitled_quantity_usd(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        filter_dict = {}
        filter_mapping = {
            "total_entitled_quantity_usd_from": "total_entitled_q_usd__gte",
            "total_entitled_quantity_usd_to": "total_entitled_q_usd__lte",
        }
        if value:
            queryset = queryset.annotate(
                total_entitled_q_usd=Coalesce(
                    Sum(
                        "payment_plans__total_entitled_quantity_usd",
                        output_field=DecimalField(),
                    ),
                    Decimal(0.0),
                )
            )
            filter_dict = {filter_mapping.get(name): value}
        return queryset.filter(**filter_dict)


class ProgramFilter(UpdatedAtFilter):
    search = filters.CharFilter(method="search_filter")
    status = filters.MultipleChoiceFilter(choices=Program.STATUS_CHOICE)
    sector = filters.MultipleChoiceFilter(choices=Program.SECTOR_CHOICE)
    number_of_households = filters.RangeFilter(method="filter_number_of_households")
    number_of_households_with_tp_in_program = filters.RangeFilter(
        method="filter_number_of_households_with_tp_in_program"
    )
    budget = filters.RangeFilter()
    start_date = filters.DateFilter(lookup_expr="gte")
    end_date = filters.DateFilter(lookup_expr="lte")
    data_collecting_type = filters.CharFilter(field_name="data_collecting_type__code", lookup_expr="exact")
    name = filters.CharFilter(lookup_expr="istartswith")
    compatible_dct = filters.CharFilter(method="compatible_dct_filter")
    beneficiary_group_match = filters.CharFilter(method="beneficiary_group_match_filter")

    class Meta:
        model = Program
        fields = (
            "search",
            "status",
            "sector",
            "number_of_households",
            "budget",
            "start_date",
            "end_date",
            "name",
            "compatible_dct",
            "beneficiary_group_match",
        )

    order_by = CustomOrderingFilter(
        fields=(
            Lower("name"),
            "status",
            "start_date",
            "end_date",
            "sector",
            "number_of_households",
            "budget",
        )
    )

    def filter_number_of_households(self, queryset: QuerySet, name: str, value: slice) -> QuerySet:
        queryset = queryset.annotate(hh_count=Count("households"))
        if min_value := value.start:
            queryset = queryset.filter(hh_count__gte=min_value)
        if max_value := value.stop:
            queryset = queryset.filter(hh_count__lte=max_value)
        return queryset

    def filter_number_of_households_with_tp_in_program(self, queryset: QuerySet, name: str, value: slice) -> QuerySet:
        queryset = queryset.annotate(
            total_hh_count=Count(
                "cycles__payment_plans__payment_items__household",
                filter=~Q(cycles__payment_plans__status=PaymentPlan.Status.TP_OPEN),
                distinct=True,
            ),
        )

        if min_value := value.start:
            queryset = queryset.filter(total_hh_count__gte=min_value)
        if max_value := value.stop:
            queryset = queryset.filter(total_hh_count__lte=max_value)

        return queryset

    def search_filter(self, qs: QuerySet, name: str, values: Any) -> QuerySet:
        q_obj = Q()
        for value in values.split(" "):
            q_obj |= Q(name__istartswith=value)
        return qs.filter(q_obj)

    def compatible_dct_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        business_area_slug = self.request.parser_context.get("kwargs", {}).get("business_area_slug")
        current_program = Program.objects.get(slug=value, business_area__slug=business_area_slug)
        return qs.filter(data_collecting_type__compatible_types=current_program.data_collecting_type).exclude(
            id=current_program.id
        )

    def beneficiary_group_match_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        business_area_slug = self.request.parser_context.get("kwargs", {}).get("business_area_slug")
        current_program = Program.objects.get(slug=value, business_area__slug=business_area_slug)
        return qs.filter(beneficiary_group=current_program.beneficiary_group).exclude(id=current_program.id)
