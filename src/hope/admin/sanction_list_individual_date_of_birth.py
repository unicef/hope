from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from models.sanction_list import SanctionListIndividualDateOfBirth


@admin.register(SanctionListIndividualDateOfBirth)
class SanctionListIndividualDateOfBirthAdmin(HOPEModelAdminBase):
    readonly_fields = ("individual",)
    list_filter = ("individual__sanction_list",)
