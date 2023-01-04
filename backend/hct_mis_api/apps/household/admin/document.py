import logging

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.combo import RelatedFieldComboFilter

from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, SoftDeletableAdminMixin

from ..models import Document, DocumentType

logger = logging.getLogger(__name__)


@admin.register(Document)
class DocumentAdmin(SoftDeletableAdminMixin, HOPEModelAdminBase):
    search_fields = ("document_number", "country")
    list_display = ("document_number", "type", "country", "status", "individual")
    raw_id_fields = ("individual",)
    list_filter = (
        ("type", RelatedFieldComboFilter),
        ("individual", AutoCompleteFilter),
        ("country", AutoCompleteFilter),
    )
    autocomplete_fields = ["type"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "type", "country")


@admin.register(DocumentType)
class DocumentTypeAdmin(HOPEModelAdminBase):
    search_fields = ("label",)
    list_display = ("label", "type")
    list_filter = (
        "type",
        "label",
    )
