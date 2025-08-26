import logging
from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.combo import RelatedFieldComboFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from hope.admin.utils import (
    HOPEModelAdminBase,
    RdiMergeStatusAdminMixin,
    SoftDeletableAdminMixin,
)
from hope.apps.core.utils import AutoCompleteFilterTemp
from hope.models.household import FOSTER_CHILD, Document, DocumentType, Individual

logger = logging.getLogger(__name__)


@admin.register(Document)
class DocumentAdmin(SoftDeletableAdminMixin, HOPEModelAdminBase, RdiMergeStatusAdminMixin):
    search_fields = ("document_number", "country__name", "individual__unicef_id")
    list_display = (
        "document_number",
        "type",
        "country",
        "status",
        "individual",
        "program",
        "cleared_by",
    )
    raw_id_fields = ("individual", "copied_from", "program", "country", "type")
    list_filter = (
        ("program__business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("type", RelatedFieldComboFilter),
        ("country", AutoCompleteFilter),
        ("individual", AutoCompleteFilterTemp),
        ("cleared_by", AutoCompleteFilter),
        "status",
    )
    autocomplete_fields = ["type"]
    exclude = ("cleared_date", "cleared_by")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("individual", "type", "country", "program")

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "individual":
            kwargs["queryset"] = Individual.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request: HttpRequest, obj: "Document", form: Any, change: bool) -> None:
        if "cleared" in form.changed_data and obj.type.type == FOSTER_CHILD:
            cleared = form.cleaned_data["cleared"]
            obj.individual.set_relationship_confirmed_flag(cleared)
            obj.cleared_by = request.user
            obj.cleared_date = timezone.now()
        return super().save_model(request, obj, form, change)


@admin.register(DocumentType)
class DocumentTypeAdmin(HOPEModelAdminBase):
    search_fields = ("label", "key")
    list_display = (
        "label",
        "key",
        "is_identity_document",
        "unique_for_individual",
        "valid_for_deduplication",
    )
    list_filter = (
        "label",
        "key",
        "is_identity_document",
        "unique_for_individual",
        "valid_for_deduplication",
    )
