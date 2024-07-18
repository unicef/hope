from django.contrib import admin

from adminfilters.combo import ChoicesFieldComboFilter

from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(PeriodicDataUpdateUpload)
class PeriodicDataUpdateUploadAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "template", "created_by", "created_at")
    list_filter = (("status", ChoicesFieldComboFilter),)


@admin.register(PeriodicDataUpdateTemplate)
class PeriodicDataUpdateTemplateAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "program", "created_by", "created_at")
    list_filter = (("status", ChoicesFieldComboFilter),)
