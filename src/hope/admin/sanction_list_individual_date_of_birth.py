from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models.sanction_list_individual_date_of_birth import SanctionListIndividualDateOfBirth


@admin.register(SanctionListIndividualDateOfBirth)
class SanctionListIndividualDateOfBirthAdmin(HOPEModelAdminBase):
    readonly_fields = ("individual",)
    list_filter = ("individual__sanction_list",)
