from typing import TYPE_CHECKING, Any

from django.db.models import Q
from django.db.models.functions import Lower

from django_filters import BooleanFilter, CharFilter, FilterSet, OrderingFilter

from hct_mis_api.apps.core.utils import CustomOrderingFilter, decode_id_string
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    PendingHousehold,
    PendingIndividual,
)

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class ImportedIndividualFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")
    duplicates_only = BooleanFilter(method="filter_duplicates_only")
    business_area = CharFilter(field_name="registration_data_import__business_area__slug")

    class Meta:
        model = PendingIndividual
        fields = ("household",)

    order_by = OrderingFilter(
        fields=(
            "mis_unicef_id",
            "id",
            "full_name",
            "birth_date",
            "sex",
            "deduplication_batch_status",
            "deduplication_golden_record_status",
        )
    )

    def filter_rdi_id(self, queryset: "QuerySet", model_field: Any, value: str) -> "QuerySet":
        return queryset.filter(registration_data_import__pk=decode_id_string(value))

    def filter_duplicates_only(self, queryset: "QuerySet", model_field: Any, value: bool) -> "QuerySet":
        if value is True:
            return queryset.filter(
                Q(deduplication_golden_record_status=DUPLICATE) | Q(deduplication_batch_status=DUPLICATE_IN_BATCH)
            )
        return queryset


class ImportedHouseholdFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")
    business_area = CharFilter(field_name="registration_data_import__business_area__slug")

    class Meta:
        model = PendingHousehold
        fields = ()

    order_by = CustomOrderingFilter(
        fields=(
            "mis_unicef_id",
            "id",
            Lower("head_of_household__full_name"),
            "size",
            "first_registration_date",
            "admin2_title",
        )
    )

    def filter_rdi_id(self, queryset: "QuerySet", model_field: Any, value: str) -> "QuerySet":
        return queryset.filter(registration_data_import__pk=decode_id_string(value))
