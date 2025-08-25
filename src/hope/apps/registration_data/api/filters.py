from django_filters import rest_framework as filters

from hope.apps.core.api.filters import UpdatedAtFilter
from models.registration_data import RegistrationDataImport


class RegistrationDataImportFilter(UpdatedAtFilter):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith",
    )

    class Meta:
        model = RegistrationDataImport
        fields = ("status", "name")
