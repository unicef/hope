from django_filters import FilterSet

from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class RegistrationDataImportFilter(FilterSet):
    class Meta:
        model = RegistrationDataImport
        fields = {
            "status": ("exact",),
            "name": ("startswith",),
        }
