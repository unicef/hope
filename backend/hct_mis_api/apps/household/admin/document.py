import logging
<<<<<<< HEAD
=======
from typing import Any
>>>>>>> origin

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
<<<<<<< HEAD
=======
from django.utils import timezone
>>>>>>> origin

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.combo import RelatedFieldComboFilter

from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, SoftDeletableAdminMixin

<<<<<<< HEAD
from ..models import Document, DocumentType
=======
from ..models import FOSTER_CHILD, Document, DocumentType
>>>>>>> origin

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
<<<<<<< HEAD
=======
    exclude = ("cleared_date", "cleared_by")
>>>>>>> origin

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "type", "country")

<<<<<<< HEAD
=======
    def save_model(self, request: HttpRequest, obj: "Document", form: Any, change: bool) -> None:
        if "cleared" in form.changed_data and obj.type.type == FOSTER_CHILD:
            cleared = form.cleaned_data["cleared"]
            obj.individual.set_relationship_confirmed_flag(cleared)
            obj.cleared_by = request.user
            obj.cleared_date = timezone.now()
        return super(DocumentAdmin, self).save_model(request, obj, form, change)

>>>>>>> origin

@admin.register(DocumentType)
class DocumentTypeAdmin(HOPEModelAdminBase):
    search_fields = ("label",)
    list_display = ("label", "type")
    list_filter = (
        "type",
        "label",
    )
