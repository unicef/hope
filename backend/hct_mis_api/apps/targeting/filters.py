from typing import TYPE_CHECKING, Any

from django.contrib.postgres.fields import IntegerRangeField
from django.db.models import Count, DateTimeField, Q
from django.db.models.functions import Lower

from django_filters import (
    BooleanFilter,
    CharFilter,
    DateTimeFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    NumericRangeFilter,
)

import hct_mis_api.apps.targeting.models as target_models
from hct_mis_api.apps.core.filters import (
    DateTimeRangeFilter,
    GlobalProgramFilterMixin,
    IntegerFilter,
)
from hct_mis_api.apps.core.utils import CustomOrderingFilter
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class HouseholdFilter(FilterSet):
    order_by = CustomOrderingFilter(
        fields=(
            "id",
            Lower("head_of_household__full_name"),
            "size",
            Lower("admin_area__name"),
            "updated_at",
            "unicef_id",
        )
    )
    business_area = CharFilter(field_name="business_area__slug")


class TargetPopulationFilter(GlobalProgramFilterMixin, FilterSet):
    """Query target population records.

    Loads associated entries for Households and TargetRules.
    """

    name = CharFilter(field_name="name", lookup_expr="startswith")
    created_by_name = CharFilter(field_name="created_by", method="filter_created_by_name")
    total_households_count_min = IntegerFilter(
        field_name="total_households_count",
        lookup_expr="gte",
    )
    total_households_count_max = IntegerFilter(
        field_name="total_households_count",
        lookup_expr="lte",
    )
    total_individuals_count_min = IntegerFilter(
        field_name="total_individuals_count",
        lookup_expr="gte",
    )
    total_individuals_count_max = IntegerFilter(
        field_name="total_individuals_count",
        lookup_expr="lte",
    )
    business_area = CharFilter(field_name="business_area__slug")
    program = ModelMultipleChoiceFilter(field_name="program", to_field_name="id", queryset=Program.objects.all())
    created_at_range = DateTimeRangeFilter(field_name="created_at")

    payment_plan_applicable = BooleanFilter(method="filter_payment_plan_applicable")
    status_not = CharFilter(field_name="status", exclude=True)

    total_households_count_with_valid_phone_no_max = IntegerFilter(
        method="filter_total_households_count_with_valid_phone_no_max"
    )
    total_households_count_with_valid_phone_no_min = IntegerFilter(
        method="filter_total_households_count_with_valid_phone_no_min"
    )

    @staticmethod
    def filter_created_by_name(queryset: "QuerySet", model_field: str, value: Any) -> "QuerySet":
        """Gets full name of the associated user from query."""
        fname_query_key = f"{model_field}__given_name__icontains"
        lname_query_key = f"{model_field}__family_name__icontains"
        for name in value.strip().split():
            queryset = queryset.filter(Q(**{fname_query_key: name}) | Q(**{lname_query_key: name}))
        return queryset

    @staticmethod
    def filter_number_of_households_min(queryset: "QuerySet", model_field: str, value: Any) -> "QuerySet":
        queryset = queryset.exclude(status=target_models.TargetPopulation.STATUS_OPEN).filter(
            number_of_households__gte=value
        )
        return queryset

    @staticmethod
    def filter_number_of_households_max(queryset: "QuerySet", model_field: str, value: Any) -> "QuerySet":
        queryset = queryset.exclude(status=target_models.TargetPopulation.STATUS_OPEN).filter(
            number_of_households__lte=value
        )
        return queryset

    @staticmethod
    def filter_total_households_count_with_valid_phone_no_max(
        queryset: "QuerySet", model_field: str, value: Any
    ) -> "QuerySet":
        queryset = queryset.annotate(
            household_count_with_phone_number=Count(
                "households",
                filter=Q(households__head_of_household__phone_no_valid=True)
                | Q(households__head_of_household__phone_no_alternative_valid=True),
            )
        ).filter(household_count_with_phone_number__lte=value)
        return queryset

    @staticmethod
    def filter_total_households_count_with_valid_phone_no_min(
        queryset: "QuerySet", model_field: str, value: Any
    ) -> "QuerySet":
        queryset = queryset.annotate(
            household_count_with_phone_number=Count(
                "households",
                filter=Q(households__head_of_household__phone_no_valid=True)
                | Q(households__head_of_household__phone_no_alternative_valid=True),
            )
        ).filter(household_count_with_phone_number__gte=value)
        return queryset

    @staticmethod
    def filter_payment_plan_applicable(queryset: "QuerySet", model_field: str, value: Any) -> "QuerySet":
        if value is True:
            return queryset.filter(
                Q(business_area__is_payment_plan_applicable=True)
                & Q(status=target_models.TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE)
            )
        return queryset

    class Meta:
        model = target_models.TargetPopulation
        fields = {
            "program": ["exact"],
            "created_at": ["exact", "lte", "gte"],
            "updated_at": ["exact", "lte", "gte"],
            "status": ["exact"],
            "households": ["exact"],
        }

        filter_overrides = {
            IntegerRangeField: {"filter_class": NumericRangeFilter},
            DateTimeField: {"filter_class": DateTimeFilter},
        }

    order_by = CustomOrderingFilter(
        fields=(
            Lower("name"),
            "created_at",
            "created_by",
            "updated_at",
            "status",
            "total_family_size",
            "program__id",
        )
    )
