"""Local replacements for smart_admin features.

These mixins and admin classes replicate the smart_admin functionality
so the project can run without django-smart-admin.
"""

import datetime
from itertools import chain

from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action, link
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import AllValuesComboFilter, PermissionPrefixFilter
from adminfilters.mixin import AdminFiltersMixin
from django.apps import apps
from django.contrib import messages
from django.contrib.admin.checks import BaseModelAdminChecks, must_be
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.admin.utils import flatten
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.management import get_contenttypes_and_models
from django.contrib.contenttypes.management.commands.remove_stale_contenttypes import (
    NoFastDeleteCollector,
)
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS, IntegrityError, OperationalError, connections, models, transaction
from django.db.models import AutoField, ForeignKey, ManyToManyField, TextField
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from hope.admin.unfold_adapter import ExtraButtonsUnfoldAdapterMixin

User = get_user_model()

TRUNCATE_CLAUSES = {
    "sqlite": [
        "DELETE FROM {table_name};",
        "DELETE FROM SQLITE_SEQUENCE WHERE name='{table_name}'",
    ],
    "postgresql": [
        'TRUNCATE TABLE "{table_name}" CASCADE;',
        "ALTER TABLE {table_name} ALTER COLUMN {pk_column} RESTART SET START 1;",
    ],
    "mysql": [
        'TRUNCATE TABLE "{table_name}" CASCADE;',
        'ALTER TABLE "{table_name}" AUTO_INCREMENT = 1',
    ],
}


def truncate_model_table(model: models.Model, reset: bool = True) -> None:
    conn = connections[model._default_manager.db]
    info = {
        "table_name": model._meta.db_table,
        "pk_column": model._meta.pk.column,
    }
    if reset:
        sqls = TRUNCATE_CLAUSES[conn.vendor][0:2]
    else:
        sqls = TRUNCATE_CLAUSES[conn.vendor][1:1]

    with conn.cursor() as cursor:
        if conn.vendor == "sqlite":
            cursor.execute("PRAGMA foreign_keys = ON")
        for tpl in sqls:
            c = tpl.format(**info)
            cursor.execute(c)


class DisplayAllMixin:
    """Replaces smart_admin.mixins.DisplayAllMixin.

    Auto-populates list_display from model fields when not explicitly set.
    """

    def get_list_display(self, request):
        if self.list_display == ("__str__",):
            return [
                field.name
                for field in self.model._meta.fields
                if not isinstance(field, AutoField | ForeignKey | TextField | ManyToManyField)
            ]
        return self.list_display


class FieldsetMixin:
    """Replaces smart_admin.mixins.FieldsetMixin.

    Supports '__others__' placeholder in fieldsets to auto-fill remaining fields.
    """

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        all_fields = self.get_fields(request, obj)
        selected = []

        if self.fieldsets:
            fieldsets = [(name, {**opts}) for name, opts in self.fieldsets]
        else:
            fieldsets = [(None, {"fields": all_fields})]

        for e in fieldsets:
            selected.extend(flatten(e[1]["fields"]))
        __all = [e for e in all_fields if e not in selected]
        for e in fieldsets:
            if e[1]["fields"] == ("__others__",):
                e[1]["fields"] = __all
        return fieldsets


class SmartModelAdminChecks(BaseModelAdminChecks):
    def _check_readonly_fields(self, obj):
        if obj.readonly_fields == ("__all__",):
            return []
        if obj.readonly_fields == ():
            return []
        if not isinstance(obj.readonly_fields, list | tuple):
            return must_be("a list or tuple", option="readonly_fields", obj=obj, id="admin.E034")
        return list(
            chain.from_iterable(
                self._check_readonly_fields_item(obj, field_name, "readonly_fields[%d]" % index)
                for index, field_name in enumerate(obj.readonly_fields)
            )
        )


class ReadOnlyMixin(UnfoldModelAdmin):
    readonly_fields: tuple[str] = ("__all__",)
    checks_class = SmartModelAdminChecks

    def get_readonly_fields(self, request, obj=None):
        if self.readonly_fields and self.readonly_fields == ("__all__",):
            return list(
                set(
                    [field.name for field in self.opts.local_fields]
                    + [field.name for field in self.opts.local_many_to_many]
                )
            )
        return self.readonly_fields


def log_truncate(request, model):
    from django.contrib.admin.models import DELETION, LogEntry

    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(model).pk,
        object_id=None,
        object_repr=f"truncate table {model._meta.verbose_name}",
        action_flag=DELETION,
        change_message="truncate table",
    )


class TruncateAdminMixin:
    truncate_table_template = "administration/truncate_table.html"

    def _truncate(self, request):
        opts = self.model._meta
        context = self.get_common_context(request, opts=opts)

        if request.method == "POST":
            with transaction.atomic():
                transaction.on_commit(lambda: log_truncate(request, self.model))
                try:
                    truncate_model_table(self.model)
                    self.message_user(request, "Table truncated", messages.SUCCESS)
                except (OperationalError, IntegrityError):
                    self.message_user(request, "Truncate failed.", messages.WARNING)
                url = reverse(admin_urlname(opts, "changelist"))
                return HttpResponseRedirect(url)
        else:
            return TemplateResponse(request, self.truncate_table_template, context)


class AutoSearchHelpTextMixin:
    """Auto-populate `search_help_text` from `search_fields` when unset."""

    def __init__(self, model: type, admin_site) -> None:
        super().__init__(model, admin_site)
        if getattr(self, "search_fields", None) and not getattr(self, "search_help_text", None):
            self.search_help_text = ", ".join(self.search_fields)


class LogEntryAdminBase(
    AutoSearchHelpTextMixin,
    ExtraButtonsUnfoldAdapterMixin,
    ExtraButtonsMixin,
    ReadOnlyMixin,
    DisplayAllMixin,
    AdminFiltersMixin,
    TruncateAdminMixin,
    UnfoldModelAdmin,
):
    """Replaces smart_admin.logs.admin.LogEntryAdmin."""

    change_list_template = None
    change_form_template = None

    list_display = ("action_time", "user", "action_flag", "content_type", "object_repr")
    readonly_fields = ("__all__",)
    search_fields = ("object_repr",)
    list_filter = (("user", AutoCompleteFilter), ("content_type", AutoCompleteFilter), "action_time", "action_flag")
    date_hierarchy = "action_time"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @link(change_list=False)
    def edit_original(self, button):
        button.href = button.original.get_admin_url()
        button.title = button.original.object_repr

    @button(html_attrs={"class": "aeb-danger"})
    def archive(self, request: HttpRequest):
        today = datetime.datetime.today()
        offset = datetime.datetime.combine(
            today - datetime.timedelta(days=365), datetime.datetime.max.time()
        ).astimezone(timezone.get_current_timezone())

        offset_label = offset.strftime("%a, %b %d %Y")
        count = LogEntry.objects.filter(action_time__lt=offset).count()

        def _doit(req: HttpRequest):
            LogEntry.objects.filter(action_time__lt=offset).delete()
            self.message_user(req, _("Records before %s have been removed") % offset_label)

        ctx = {"original": None, "offset": offset_label}

        return confirm_action(
            self,
            request,
            _doit,
            message="",
            description=_("{count} log entries will be deleted").format(count=count),
            success_message="",
            extra_context=ctx,
            template="administration/logentry/archive.html",
        )

    @button(label="Truncate", html_attrs={"class": "btn-danger"})
    def truncate(self, request):
        return super()._truncate(request)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "content_type")


class ContentTypeAdmin(
    AutoSearchHelpTextMixin, ExtraButtonsUnfoldAdapterMixin, ExtraButtonsMixin, AdminFiltersMixin, UnfoldModelAdmin
):
    """Replaces smart_admin.smart_auth.admin.ContentTypeAdmin."""

    change_list_template = None
    change_form_template = None

    list_display = ("app_label", "model")
    search_fields = ("model",)
    list_filter = (("app_label", AllValuesComboFilter),)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @button(permission="contenttypes.delete_contenttype")
    def check_stale(self, request):
        context = self.get_common_context(request, title="Stale")
        to_remove: dict[ContentType, models.Model] = {}
        if request.method == "POST":
            cts = request.POST.getlist("ct")
            with transaction.atomic():
                ContentType.objects.filter(id__in=cts).delete()
            self.message_user(request, f"Removed {len(cts)} stale ContentTypes")
        else:

            def _collect_linked(ct):
                collector = NoFastDeleteCollector(using=DEFAULT_DB_ALIAS)
                collector.collect([ct])
                for objs in collector.data.values():
                    if objs == {ct}:
                        continue
                    for o in objs:
                        try:
                            to_remove[ct].append(f"{o.__class__.__name__} {o.pk} - {str(o)}")
                        except AttributeError:
                            to_remove[ct].append(f"{o.__class__.__name__} {o.pk}")

            for app_config in apps.get_app_configs():
                content_types, app_models = get_contenttypes_and_models(app_config, DEFAULT_DB_ALIAS, ContentType)
                if not app_models:
                    continue
                for model_name, ct in content_types.items():
                    if model_name not in app_models:
                        to_remove[ct] = []
                        _collect_linked(ct)

            for ct in ContentType.objects.all():
                if ct.app_label not in apps.app_configs and ct not in to_remove:
                    to_remove[ct] = []
                    _collect_linked(ct)

            context["to_remove"] = dict(sorted(to_remove.items(), key=lambda x: f"{x[0].app_label} {x[0].model}"))
            return TemplateResponse(request, "administration/contenttype/stale.html", context)
        return None


class PermissionAdmin(
    AutoSearchHelpTextMixin, ExtraButtonsUnfoldAdapterMixin, ExtraButtonsMixin, AdminFiltersMixin, UnfoldModelAdmin
):
    """Replaces smart_admin.smart_auth.admin.PermissionAdmin."""

    change_list_template = None
    change_form_template = None

    list_display = ("name", "content_type", "codename")
    search_fields = ("name",)
    list_filter = (
        ("content_type", AutoCompleteFilter),
        PermissionPrefixFilter,
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @button(label="Users/Groups")
    def users(self, request, pk):
        context = self.get_common_context(request, pk, aeu_groups=["1"])
        perm = context["original"]
        from django.db.models import Q

        users = User.objects.filter(Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()
        groups = Group.objects.filter(permissions=perm).distinct()
        context["title"] = _('Users/Groups with "%s"') % perm.name
        context["user_opts"] = User._meta
        context["data"] = {"users": users, "groups": groups}
        return render(request, "administration/auth/permission/users.html", context)
