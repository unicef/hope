from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.sanction_list.models import (
    SanctionListIndividualDocument,
)


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
