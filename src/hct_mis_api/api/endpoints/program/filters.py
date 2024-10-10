from django.db.models.query import QuerySet

from django_filters import BooleanFilter, CharFilter, DateFromToRangeFilter
from django_filters.rest_framework import FilterSet

from hct_mis_api.apps.program.models import Program


class ProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug")
    active = BooleanFilter(method="is_active_filter")
    updated_at = DateFromToRangeFilter()

    class Meta:
        model = Program
        fields = (
            "business_area",
            "active",
            "updated_at",
            "status",
        )

    def is_active_filter(self, queryset: "QuerySet[Program]", name: str, value: bool) -> "QuerySet[Program]":
        if value is True:
            return queryset.filter(status=Program.ACTIVE)
        elif value is False:
            return queryset.exclude(status=Program.ACTIVE)
        return queryset
