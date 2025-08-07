from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.sanction_list.models import (
    SanctionListIndividualCountries,
)


@admin.register(SanctionListIndividualCountries)
class SanctionListIndividualCountriesAdmin(HOPEModelAdminBase):
    list_filter = ("individual__sanction_list",)
