from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models.sanction_list import SanctionListIndividualAliasName


@admin.register(SanctionListIndividualAliasName)
class SanctionListIndividualAliasNameAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "individual",
    )
    readonly_fields = ("individual", "name")
    list_filter = ("individual__sanction_list",)
