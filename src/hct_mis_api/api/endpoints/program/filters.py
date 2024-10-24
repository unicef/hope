from django.db.models.query import QuerySet

from django_filters import BooleanFilter, CharFilter

from hct_mis_api.apps.core.api.filters import UpdatedAtFilter
from hct_mis_api.apps.program.models import Program


class ProgramFilter(UpdatedAtFilter):
    business_area = CharFilter(field_name="business_area__slug")
    active = BooleanFilter(method="is_active_filter")

    class Meta:
        model = Program
        fields = (
            "business_area",
            "active",
            "status",
        )

    def is_active_filter(self, queryset: "QuerySet[Program]", name: str, value: bool) -> "QuerySet[Program]":
        if value is True:
            return queryset.filter(status=Program.ACTIVE)
        return queryset.exclude(status=Program.ACTIVE)
