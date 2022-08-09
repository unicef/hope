from django.db.models import Q
from django.db.models.functions import Lower
from django_filters import BooleanFilter, CharFilter, FilterSet, OrderingFilter

from hct_mis_api.apps.core.utils import CustomOrderingFilter, decode_id_string
from hct_mis_api.apps.household.models import DUPLICATE
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual, DUPLICATE_IN_BATCH, ImportedHousehold


class ImportedIndividualFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")
    duplicates_only = BooleanFilter(method="filter_duplicates_only")
    business_area = CharFilter(field_name="registration_data_import__business_area_slug")

    class Meta:
        model = ImportedIndividual
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

    def filter_rdi_id(self, queryset, model_field, value):
        return queryset.filter(registration_data_import__hct_id=decode_id_string(value))

    def filter_duplicates_only(self, queryset, model_field, value):
        if value is True:
            return queryset.filter(
                Q(deduplication_golden_record_status=DUPLICATE) | Q(deduplication_batch_status=DUPLICATE_IN_BATCH)
            )
        return queryset


class ImportedHouseholdFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")
    business_area = CharFilter(field_name="registration_data_import__business_area_slug")

    class Meta:
        model = ImportedHousehold
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

    def filter_rdi_id(self, queryset, model_field, value):
        return queryset.filter(registration_data_import__hct_id=decode_id_string(value))
