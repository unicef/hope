import logging
from typing import TYPE_CHECKING

from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.http import (
    HttpRequest,
)
from admin_sync.mixin import GetManyFromRemoteMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from adminfilters.mixin import AdminFiltersMixin
from jsoneditor.forms import JSONEditor

from hct_mis_api.admin.utils import (
    SoftDeletableAdminMixin,
)
from hct_mis_api.apps.core.models import (
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
    PeriodicFieldData,
)
from mptt.admin import MPTTModelAdmin

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


logger = logging.getLogger(__name__)


class FlexibleAttributeInline(admin.TabularInline):
    model = FlexibleAttribute
    fields = readonly_fields = ("name", "associated_with", "required")
    extra = 0


@admin.register(FlexibleAttribute)
class FlexibleAttributeAdmin(AdminFiltersMixin, GetManyFromRemoteMixin, SoftDeletableAdminMixin):
    list_display = ("name", "type", "required", "program", "pdu_data", "group")
    list_filter = (
        ("type", ChoicesFieldComboFilter),
        ("associated_with", ChoicesFieldComboFilter),
        "required",
        ("group", AutoCompleteFilter),
    )
    search_fields = ("name",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
    raw_id_fields = ("group", "program", "pdu_data")

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return super().get_queryset(request).select_related("group", "program", "pdu_data")


@admin.register(PeriodicFieldData)
class PeriodicFieldDataAdmin(admin.ModelAdmin):
    list_filter = ("subtype", "number_of_rounds")
    list_display = ("__str__", "subtype", "number_of_rounds")


@admin.register(FlexibleAttributeGroup)
class FlexibleAttributeGroupAdmin(AdminFiltersMixin, GetManyFromRemoteMixin, SoftDeletableAdminMixin, MPTTModelAdmin):
    inlines = (FlexibleAttributeInline,)
    list_display = ("name", "parent", "required", "repeatable", "is_removed")
    # autocomplete_fields = ("parent",)
    raw_id_fields = ("parent",)
    list_filter = (
        ("parent", AutoCompleteFilter),
        "repeatable",
        "required",
    )
    search_fields = ("name",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }


@admin.register(FlexibleAttributeChoice)
class FlexibleAttributeChoiceAdmin(GetManyFromRemoteMixin, SoftDeletableAdminMixin):
    list_display = (
        "list_name",
        "name",
    )
    search_fields = ("name", "list_name")
    filter_horizontal = ("flex_attributes",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
