from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from admin_extra_buttons.api import button
from adminfilters.autocomplete import AutoCompleteFilter

from hct_mis_api.apps.sanction_list.models import (
    SanctionList,
    SanctionListIndividual,
    SanctionListIndividualAliasName,
    SanctionListIndividualCountries,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualDocument,
    SanctionListIndividualNationalities,
    UploadedXLSXFile,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class SanctionListIndividualDateOfBirthInline(admin.StackedInline):
    model = SanctionListIndividualDateOfBirth
    extra = 0


@admin.register(SanctionList)
class SanctionListAdmin(HOPEModelAdminBase):
    list_display = ("name",)

    @button()
    def refresh(self, request: HttpRequest, pk: str) -> None:
        sl = SanctionList.objects.get(pk=pk)
        sl.strategy.refresh()


@admin.register(SanctionListIndividual)
class SanctionListIndividualAdmin(HOPEModelAdminBase):
    list_display = (
        "full_name",
        "listed_on",
        "un_list_type",
        "sanction_list",
        "country_of_birth",
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


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(HOPEModelAdminBase):
    list_display = (
        "document_number",
        "type_of_document",
        "date_of_issue",
        "issuing_country",
    )
    raw_id_fields = ("individual", "issuing_country")
    list_filter = (("issuing_country", AutoCompleteFilter), "type_of_document")
    search_fields = ("document_number",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "issuing_country")


@admin.register(SanctionListIndividualNationalities)
class SanctionListIndividualNationalitiesAdmin(HOPEModelAdminBase):
    pass


@admin.register(SanctionListIndividualCountries)
class SanctionListIndividualCountriesAdmin(HOPEModelAdminBase):
    pass


@admin.register(SanctionListIndividualAliasName)
class SanctionListIndividualAliasNameAdmin(HOPEModelAdminBase):
    pass


@admin.register(SanctionListIndividualDateOfBirth)
class SanctionListIndividualDateOfBirthAdmin(HOPEModelAdminBase):
    pass


@admin.register(UploadedXLSXFile)
class UploadedXLSXFileAdmin(HOPEModelAdminBase):
    pass
