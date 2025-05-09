from typing import Any

from django.db.models import Count, Q, QuerySet
from django.db.models.functions import Lower

from django_filters import CharFilter, DateFilter, FilterSet

from hct_mis_api.apps.core.filters import (
    DateTimeRangeFilter,
    IntegerFilter,
    IntegerRangeFilter,
)
from hct_mis_api.apps.core.utils import CustomOrderingFilter
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class RegistrationDataImportFilter(FilterSet):
    import_date = DateFilter(field_name="import_date__date")
    import_date_range = DateTimeRangeFilter(field_name="import_date")
    size = IntegerRangeFilter(field_name="number_of_households")
    total_households_count_with_valid_phone_no_max = IntegerFilter(
        method="filter_total_households_count_with_valid_phone_no_max"
    )
    total_households_count_with_valid_phone_no_min = IntegerFilter(
        method="filter_total_households_count_with_valid_phone_no_min"
    )
    search = CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )

    class Meta:
        model = RegistrationDataImport
        fields = {
            "imported_by__id": ["exact"],
            "import_date": ["exact"],
            "status": ["exact"],
            "name": ["exact", "startswith"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            Lower("name"),
            "status",
            "import_date",
            "number_of_individuals",
            "number_of_households",
            "data_source",
            Lower("imported_by__first_name"),
        )
    )

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        qs = super().filter_queryset(queryset)
        return qs.exclude(excluded=True)

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
