from django.db.models import Q
from django.db.models.functions import Lower

from django_filters import (
    CharFilter,
    DateTimeFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    NumericRangeFilter,
)

import hct_mis_api.apps.targeting.models as target_models
from hct_mis_api.apps.core.filters import DateRangeFilter, IntegerFilter
from hct_mis_api.apps.core.utils import CustomOrderingFilter
from hct_mis_api.apps.program.models import Program


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


class TargetPopulationFilter(FilterSet):
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
    created_at_range = DateRangeFilter(field_name="created_at__date")

    @staticmethod
    def filter_created_by_name(queryset, model_field, value):
        """Gets full name of the associated user from query."""
        fname_query_key = f"{model_field}__given_name__icontains"
        lname_query_key = f"{model_field}__family_name__icontains"
        for name in value.strip().split():
            queryset = queryset.filter(Q(**{fname_query_key: name}) | Q(**{lname_query_key: name}))
        return queryset

    class Meta:
        model = target_models.TargetPopulation
        fields = (
            "name",
            "created_by_name",
            "created_at",
            "updated_at",
            "status",
            "households",
        )

        filter_overrides = {
            target_models.IntegerRangeField: {"filter_class": NumericRangeFilter},
            target_models.models.DateTimeField: {"filter_class": DateTimeFilter},
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
