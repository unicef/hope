import logging

from admin_sync.mixin import GetManyFromRemoteMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from jsoneditor.forms import JSONEditor
from mptt.admin import MPTTModelAdmin

from hope.admin.utils import SoftDeletableAdminMixin
from hope.models.core import FlexibleAttribute, FlexibleAttributeGroup

logger = logging.getLogger(__name__)


class FlexibleAttributeInline(admin.TabularInline):
    model = FlexibleAttribute
    fields = readonly_fields = ("name", "associated_with", "required")
    extra = 0


@admin.register(FlexibleAttributeGroup)
class FlexibleAttributeGroupAdmin(AdminFiltersMixin, GetManyFromRemoteMixin, SoftDeletableAdminMixin, MPTTModelAdmin):
    inlines = (FlexibleAttributeInline,)
    list_display = ("name", "parent", "required", "repeatable", "is_removed")
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
