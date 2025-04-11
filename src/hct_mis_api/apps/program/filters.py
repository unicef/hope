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


# TODO: delete with GraphQL
class ProgramFilter(FilterSet):
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=Program.STATUS_CHOICE)
    sector = MultipleChoiceFilter(field_name="sector", choices=Program.SECTOR_CHOICE)
    number_of_households = IntegerRangeFilter(method="filter_number_of_households")
    number_of_households_with_tp_in_program = IntegerRangeFilter(
        method="filter_number_of_households_with_tp_in_program"
    )
    budget = DecimalRangeFilter(field_name="budget")
    start_date = DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = DateFilter(field_name="end_date", lookup_expr="lte")
    data_collecting_type = CharFilter(field_name="data_collecting_type__code", lookup_expr="exact")
    name = CharFilter(field_name="name", lookup_expr="istartswith")
    compatible_dct = BooleanFilter(method="compatible_dct_filter")
    beneficiary_group_match = BooleanFilter(method="beneficiary_group_match_filter", required=True)

    class Meta:
        model = Program
        fields = (
            "business_area",
            "search",
            "status",
            "sector",
            "number_of_households",
            "budget",
            "start_date",
            "end_date",
            "name",
            "beneficiary_group_match",
        )

    order_by = CustomOrderingFilter(
        fields=(Lower("name"), "status", "start_date", "end_date", "sector", "number_of_households", "budget")
    )

    def filter_number_of_households(self, queryset: QuerySet, name: str, value: Dict) -> QuerySet:
        queryset = queryset.annotate(hh_count=Count("household"))
        if min_value := value.get("min"):
            queryset = queryset.filter(hh_count__gte=min_value)
        if max_value := value.get("max"):
            queryset = queryset.filter(hh_count__lte=max_value)

        return queryset

    def filter_number_of_households_with_tp_in_program(self, queryset: QuerySet, name: str, value: Dict) -> QuerySet:
        queryset = queryset.annotate(
            total_hh_count=Count(
                "household_count",
                filter=~Q(cycles__payment_plans__status=PaymentPlan.Status.TP_OPEN),
                distinct=True,
            ),
        )

        if min_value := value.get("min"):
            queryset = queryset.filter(total_hh_count__gte=min_value)
        if max_value := value.get("max"):
            queryset = queryset.filter(total_hh_count__lte=max_value)

        return queryset

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(name__istartswith=value)
        return qs.filter(q_obj)

    def compatible_dct_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        program_id = get_program_id_from_headers(self.request.headers)
        if value and program_id:
            current_program = Program.objects.get(id=program_id)
            return qs.filter(data_collecting_type__compatible_types=current_program.data_collecting_type).exclude(
                id=program_id
            )
        return qs

    def beneficiary_group_match_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        program_id = get_program_id_from_headers(self.request.headers)
        if value and program_id:
            current_program = Program.objects.get(id=program_id)
            return qs.filter(beneficiary_group=current_program.beneficiary_group).exclude(id=program_id)
        return qs


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
