import logging

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib.admin import register
from django.http import HttpRequest
from import_export import fields
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget
from smart_admin.mixins import LinkedObjectsMixin

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.steficon.forms import RuleCommitAdminForm
from hope.apps.utils.security import is_root
from hope.models.rule import Rule, RuleCommit
from hope.models.user import User

from .steficon import TestRuleMixin

logger = logging.getLogger(__name__)


class RuleCommitResource(ModelResource):
    rule = fields.Field(column_name="rule", attribute="rule", widget=ForeignKeyWidget(Rule, "name"))
    updated_by = fields.Field(
        column_name="updated_by",
        attribute="created_by",
        widget=ForeignKeyWidget(User, "username"),
    )

    class Meta:
        model = RuleCommit
        fields = (
            "timestamp",
            "rule",
            "version",
            "updated_by",
            "affected_fields",
            "is_release",
        )
        import_id_fields = ("rule", "version")


@register(RuleCommit)
class RuleCommitAdmin(ImportExportMixin, LinkedObjectsMixin, TestRuleMixin, HOPEModelAdminBase):
    list_display = (
        "rule",
        "version",
        "updated_by",
        "timestamp",
        "is_release",
        "enabled",
        "deprecated",
        "language",
    )
    list_filter = (
        ("rule", AutoCompleteFilter),
        ("updated_by", AutoCompleteFilter),
        "is_release",
        "enabled",
        "deprecated",
        "language",
    )
    search_fields = ("rule__name",)
    readonly_fields = ("updated_by",)
    change_form_template = None
    change_list_template = None
    resource_class = RuleCommitResource
    form = RuleCommitAdminForm
    fields = (
        "version",
        "rule",
        "definition",
        "is_release",
        "enabled",
        "deprecated",
        "language",
        "affected_fields",
        "updated_by",
    )
    date_hierarchy = "timestamp"

    def get_queryset(self, request: HttpRequest) -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related(
                "rule",
                "updated_by",
            )
        )

    def get_readonly_fields(self, request: HttpRequest, obj: RuleCommit | None = None) -> list[str]:
        if is_root(request):
            return ["updated_by"]
        return ["updated_by", "version", "rule"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return is_root(request)
