from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from django.db.models import JSONField
from jsoneditor.forms import JSONEditor
from smart_admin.decorators import smart_register

from hope.contrib.aurora import models


@smart_register(models.Registration)
class RegistrationAdmin(AdminFiltersMixin, ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "project", "rdi_policy")
    readonly_fields = ("name", "project", "slug", "extra", "metadata")
    list_filter = ("rdi_policy", ("project", AutoCompleteFilter))
    search_fields = ("name",)
    raw_id_fields = ("steficon_rule",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
