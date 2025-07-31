from django.contrib import admin

from hct_mis_api.admin.utils import HOPEModelAdminBase
from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividualAliasName,
)


@admin.register(SanctionListIndividualAliasName)
class SanctionListIndividualAliasNameAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "individual",
    )
    readonly_fields = ("individual", "name")
    list_filter = ("individual__sanction_list",)
