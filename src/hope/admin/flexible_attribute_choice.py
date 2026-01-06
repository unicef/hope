import logging

from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from jsoneditor.forms import JSONEditor

from hope.admin.utils import SoftDeletableAdminMixin
from hope.models import FlexibleAttributeChoice

logger = logging.getLogger(__name__)


@admin.register(FlexibleAttributeChoice)
class FlexibleAttributeChoiceAdmin(SoftDeletableAdminMixin):
    list_display = (
        "list_name",
        "name",
    )
    search_fields = ("name", "list_name")
    filter_horizontal = ("flex_attributes",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
