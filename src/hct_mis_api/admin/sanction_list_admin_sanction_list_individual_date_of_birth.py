from django.contrib import admin

from hct_mis_api.admin.utils_admin import HOPEModelAdminBase
from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividualDateOfBirth,
)


@admin.register(SanctionListIndividualDateOfBirth)
class SanctionListIndividualDateOfBirthAdmin(HOPEModelAdminBase):
    readonly_fields = ("individual",)
    list_filter = ("individual__sanction_list",)
