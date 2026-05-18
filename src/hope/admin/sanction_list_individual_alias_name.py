from django.contrib import admin
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import SanctionListIndividualAliasName


@admin.register(SanctionListIndividualAliasName)
class SanctionListIndividualAliasNameAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "individual",
    )
    readonly_fields = ("individual", "name")
    list_filter = ("individual__sanction_list",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
