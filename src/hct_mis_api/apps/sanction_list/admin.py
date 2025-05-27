from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter

from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualDocument,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class SanctionListIndividualDateOfBirthAdmin(admin.StackedInline):
    model = SanctionListIndividualDateOfBirth
    extra = 0


@admin.register(SanctionListIndividual)
class SanctionListIndividualAdmin(HOPEModelAdminBase):
    list_display = ("full_name", "listed_on", "un_list_type", "reference_number", "country_of_birth", "active")
    search_fields = (
        "full_name",
        "first_name",
        "second_name",
        "third_name",
        "fourth_name",
        "name_original_script",
        "reference_number",
    )
    list_filter = ("un_list_type", "active", ("country_of_birth", AutoCompleteFilter))
    inlines = (SanctionListIndividualDateOfBirthAdmin,)
    raw_id_fields = ("country_of_birth",)


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(HOPEModelAdminBase):
    list_display = ("document_number", "type_of_document", "date_of_issue", "issuing_country")
    raw_id_fields = ("individual", "issuing_country")
    list_filter = (("issuing_country", AutoCompleteFilter), "type_of_document")
    search_fields = ("document_number",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "issuing_country")
