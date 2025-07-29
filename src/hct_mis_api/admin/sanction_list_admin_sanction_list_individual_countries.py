from django.contrib import admin

from hct_mis_api.admin.utils_admin import HOPEModelAdminBase
from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividualCountries,
)


@admin.register(SanctionListIndividualCountries)
class SanctionListIndividualCountriesAdmin(HOPEModelAdminBase):
    list_filter = ("individual__sanction_list",)
