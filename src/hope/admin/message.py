from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import Message


class MessageRecipientMapInline(admin.TabularInline):
    model = Message.households.through
    extra = 0
    list_prefetch_related = ("household__head_of_household",)
    fields: tuple[str, ...] | None = ("get_hoh_name",)
    readonly_fields: tuple[str, ...] = ("get_hoh_name",)

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def get_hoh_name(self, obj: Any) -> str:
        return obj.household.head_of_household.full_name

    get_hoh_name.short_description = "HoH Full Name"


class MessageCopiedToInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ("unicef_id",)
    readonly_fields = ("unicef_id",)
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Message representations"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return Message.objects.all()  # pragma: no cover


@admin.register(Message)
class MessageAdmin(AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    exclude = (
        "number_of_recipients",
        "unicef_id",
        "full_list_arguments",
        "random_sampling_arguments",
        "households",
    )
    inlines = [MessageRecipientMapInline, MessageCopiedToInline]
    list_select_related: bool | tuple[str, ...] = ("created_by",)
    list_prefetch_related: bool | tuple[str, ...] = ("recipients",)
    readonly_fields: tuple[str, ...] = (
        "title",
        "body",
        "business_area",
        "program",
        "payment_plan",
        "registration_data_import",
        "sampling_type",
        "sample_size",
        "created_by",
        "copied_from",
    )
    list_display = (
        "unicef_id",
        "title",
        "sampling_type",
        "sample_size",
        "created_by",
        "registration_data_import",
        "number_of_recipients",
    )
    list_filter = (("created_by", AutoCompleteFilter), "created_at", "sampling_type")
    raw_id_fields = ["created_by", "payment_plan", "program", "copied_from"]
    filter_horizontal = ["households"]
    search_fields = ("unicef_id",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model.objects.get_queryset()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
