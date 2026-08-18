from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import AccountAttachment


@admin.register(AccountAttachment)
class AccountAttachmentAdmin(HOPEModelAdminBase):
    list_display = ("account", "title", "uploaded_at", "created_by")
    list_filter = (("account__account_type", AutoCompleteFilter),)
    raw_id_fields = ("account", "created_by")
    readonly_fields = ("uploaded_at",)
    date_hierarchy = "uploaded_at"
    search_fields = ("title",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super().get_queryset(request).select_related("account__account_type", "account__individual", "created_by")
        )
