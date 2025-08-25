from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from smart_admin.mixins import LinkedObjectsMixin

from hope.admin.utils import HOPEModelAdminBase
from models.sanction_list import (
    SanctionListIndividual,
    SanctionListIndividualDateOfBirth,
)


class SanctionListIndividualDateOfBirthInline(admin.StackedInline):
    model = SanctionListIndividualDateOfBirth
    extra = 0


@admin.register(SanctionListIndividual)
class SanctionListIndividualAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = (
        "sanction_list",
        "full_name",
        "listed_on",
        "reference_number",
        # "un_list_type",
        # "country_of_birth",
        "active",
    )
    search_fields = (
        "full_name",
        "first_name",
        "second_name",
        "third_name",
        "fourth_name",
        "name_original_script",
        "reference_number",
    )
    list_filter = (
        "sanction_list",
        "un_list_type",
        "active",
        ("country_of_birth", AutoCompleteFilter),
    )
    inlines = (SanctionListIndividualDateOfBirthInline,)
    raw_id_fields = ("country_of_birth",)
    readonly_fields = ("sanction_list", "reference_number", "data_id")
