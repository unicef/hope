from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase
from hope.models import Message


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
    inlines = [MessageCopiedToInline]
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
    search_fields = ("unicef_id",)

    @button(permission="accountability.view_message")
    def recipient_households(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:
        url = reverse("admin:household_household_changelist")
        return HttpResponseRedirect(f"{url}?qs=messages__id={pk}&qs__negate=false")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model.objects.get_queryset()
