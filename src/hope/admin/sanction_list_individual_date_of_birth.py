from django.contrib import admin
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import SanctionListIndividualDateOfBirth


@admin.register(SanctionListIndividualDateOfBirth)
class SanctionListIndividualDateOfBirthAdmin(HOPEModelAdminBase):
    readonly_fields = ("individual",)
    list_filter = ("individual__sanction_list",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
