from django_filters import rest_framework as filters

from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class RegistrationDataImportFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )

    class Meta:
        model = RegistrationDataImport
        fields = ("status", "name")
