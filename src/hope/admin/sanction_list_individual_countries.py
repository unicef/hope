from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models.sanction_list_individual_countries import SanctionListIndividualCountries


@admin.register(SanctionListIndividualCountries)
class SanctionListIndividualCountriesAdmin(HOPEModelAdminBase):
    list_filter = ("individual__sanction_list",)
