from adminfilters.filters import ChoicesFieldComboFilter
from django.contrib import admin

from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(RegistrationDataImport)
class RegistrationDataImportAdmin(HOPEModelAdminBase):
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("data_source", ChoicesFieldComboFilter),
    )
    date_hierarchy = "updated_at"
