from typing import Any, Optional, Sequence, Union

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin

from hct_mis_api.apps.accountability.models import Message, Feedback, Survey
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, IsOriginalAdminMixin


class MessageRecipientMapInline(admin.TabularInline):
    model = Message.households.through
    extra = 0
    list_prefetch_related = ("household__head_of_household",)
    fields: Optional[Sequence[str]] = ("get_hoh_name",)
    readonly_fields: Sequence[str] = ("get_hoh_name",)

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
        return Message.original_and_repr_objects.all()


@admin.register(Message)
class MessageAdmin(AdminAdvancedFiltersMixin, HOPEModelAdminBase, IsOriginalAdminMixin):
    exclude = (
        "number_of_recipients",
        "unicef_id",
        "full_list_arguments",
        "random_sampling_arguments",
        "households",
    )
    inlines = [MessageRecipientMapInline, MessageCopiedToInline]
    list_select_related: Union[bool, Sequence[str]] = ("created_by",)
    list_prefetch_related: Union[bool, Sequence[str]] = ("recipients",)
    readonly_fields: Sequence[str] = (
        "title",
        "body",
        "business_area",
        "registration_data_import",
        "sampling_type",
        "sample_size",
    )
    list_filter = (
        ("created_by", AutoCompleteFilter),
        "created_at",
    )
    raw_id_fields = ["created_by", "target_population", "program"]
    filter_horizontal = ["households"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model.original_and_repr_objects.get_queryset()


@admin.register(Survey)
class SurveyAdmin(HOPEModelAdminBase):
    pass


@admin.register(Feedback)
class FeedbackAdmin(HOPEModelAdminBase):
    pass
