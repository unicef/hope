from typing import Dict

from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponseRedirect

from admin_extra_buttons.api import button, confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from smart_admin.mixins import LinkedObjectsMixin

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
from hct_mis_api.admin.utils_admin import HOPEModelAdminBase


class SanctionListIndividualDateOfBirthInline(admin.StackedInline):
    model = SanctionListIndividualDateOfBirth
    extra = 0


@admin.register(SanctionList)
class SanctionListAdmin(HOPEModelAdminBase):
    list_display = ("name",)

    @button()
    def refresh(self, request: HttpRequest, pk: str) -> None:
        try:
            sl = SanctionList.objects.get(pk=pk)
            sl.strategy.refresh()
            self.message_user(request, "Sanction List refreshed", messages.SUCCESS)
        except KeyError:
            self.message_user(request, "Configuration Problem", messages.ERROR)

    @button()
    def empty(self, request: HttpRequest, pk: str) -> None:
        sl = SanctionList.objects.get(pk=pk)

        def _delete(request: HttpRequest) -> HttpResponseRedirect:
            sl.entries.all().delete()
            return HttpResponseRedirect("..")

        return confirm_action(
            self,
            request,
            action=_delete,
            message="Continuing will delete all entries in this list",
            success_message="Sanction List emptied.",
            title="Empty sanction list",
        )


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


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(HOPEModelAdminBase):
    list_display = (
        "document_number",
        "type_of_document",
        "date_of_issue",
        "issuing_country",
    )
    raw_id_fields = ("individual", "issuing_country")
    list_filter = (
        "individual__sanction_list",
        ("issuing_country", AutoCompleteFilter),
        "type_of_document",
    )
    search_fields = ("document_number",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "issuing_country")


@admin.register(SanctionListIndividualNationalities)
class SanctionListIndividualNationalitiesAdmin(HOPEModelAdminBase):
    list_display = ("nationality", "individual")
    readonly_fields = ("nationality", "individual")
    list_filter = ("individual__sanction_list",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "nationality")


@admin.register(SanctionListIndividualCountries)
class SanctionListIndividualCountriesAdmin(HOPEModelAdminBase):
    list_filter = ("individual__sanction_list",)


@admin.register(SanctionListIndividualAliasName)
class SanctionListIndividualAliasNameAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "individual",
    )
    readonly_fields = ("individual", "name")
    list_filter = ("individual__sanction_list",)


@admin.register(SanctionListIndividualDateOfBirth)
class SanctionListIndividualDateOfBirthAdmin(HOPEModelAdminBase):
    readonly_fields = ("individual",)
    list_filter = ("individual__sanction_list",)


@admin.register(UploadedXLSXFile)
class UploadedXLSXFileAdmin(HOPEModelAdminBase):
    list_display = ("id", "file", "associated_email")
    filter_horizontal = ("selected_lists",)

    def get_actions(self, request: HttpRequest) -> Dict:
        return super().get_actions(request)
