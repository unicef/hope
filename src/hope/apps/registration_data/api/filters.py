from django_filters import rest_framework as filters

from hope.apps.core.api.filters import UpdatedAtFilter
from hope.apps.registration_data.models import RegistrationDataImport


class RegistrationDataImportFilter(UpdatedAtFilter):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )

    class Meta:
        model = RegistrationDataImport
        fields = ("status", "name")
