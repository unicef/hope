import logging
from typing import TYPE_CHECKING

from admin_sync.mixin import GetManyFromRemoteMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.http import HttpRequest
from jsoneditor.forms import JSONEditor

from hope.admin.utils import SoftDeletableAdminMixin
from models.core import FlexibleAttribute

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


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
