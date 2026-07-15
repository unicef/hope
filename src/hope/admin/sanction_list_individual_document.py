from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import SanctionListIndividualDocument


@admin.register(SanctionListIndividualDocument)
class SanctionListIndividualDocumentAdmin(HOPEModelAdminBase):
    list_display = (
        "document_number",
        "type_of_document",
        "date_of_issue",
        "issuing_country",
    )
    list_filter = (
        "individual__sanction_list",
        ("issuing_country", AutoCompleteFilter),
        "type_of_document",
    )
    readonly_fields = ("individual",)
    search_fields = ("document_number",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "issuing_country")
