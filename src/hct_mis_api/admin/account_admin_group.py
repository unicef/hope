import logging
from typing import Any

from django.contrib import admin
from django.contrib.admin.utils import construct_change_message
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as _GroupAdmin
from django.contrib.auth.models import Group, Permission
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from admin_extra_buttons.decorators import button
from admin_sync.mixin import GetManyFromRemoteMixin, SyncMixin
from adminactions.export import ForeignKeysCollector
from adminfilters.autocomplete import AutoCompleteFilter
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ManyToManyWidget
from smart_admin.decorators import smart_register

from hct_mis_api.admin.utils_admin import HOPEModelAdminBase, HopeModelAdminMixin
from hct_mis_api.apps.account import models as account_models

logger = logging.getLogger(__name__)


class GroupResource(resources.ModelResource):
    permissions = fields.Field(widget=ManyToManyWidget(Permission, field="codename"), attribute="permissions")

    class Meta:
        model = Group
        fields = ("name", "permissions")
        import_id_fields = ("name",)


@smart_register(Group)
class GroupAdmin(ImportExportModelAdmin, SyncMixin, HopeModelAdminMixin, _GroupAdmin):
    resource_class = GroupResource
    change_list_template = "admin/account/group/change_list.html"

    @button(permission=lambda request, group: request.user.is_superuser)
    def import_fixture(self, request: HttpRequest) -> TemplateResponse:
        from adminactions.helpers import import_fixture as _import_fixture

        return _import_fixture(self, request)

    def _perms(self, request: HttpRequest, object_id: str) -> set:
        return set(self.get_object(request, object_id).permissions.values_list("codename", flat=True))

    @button(permission="auth.view_group")
    def users(self, request: HttpRequest, pk: str) -> HttpResponse:
        User = get_user_model()
        context = self.get_common_context(request, pk, aeu_groups=["1"])
        group = context["original"]
        users = User.objects.filter(groups=group).distinct()
        context["title"] = _('Users in group "{}"').format(group.name)
        context["user_opts"] = User._meta
        context["data"] = users
        return render(request, "admin/account/group/members.html", context)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict | None = None,
    ) -> HttpResponse:
        if object_id:
            self.existing_perms = self._perms(request, object_id)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def construct_change_message(self, request: HttpRequest, form: Any, formsets: Any, add: bool = False) -> list[dict]:
        change_message = construct_change_message(form, formsets, add)
        if not add and "permissions" in form.changed_data:
            new_perms = self._perms(request, form.instance.id)
            changed: dict[str, Any] = change_message[0]["changed"]
            changed["permissions"] = {
                "added": sorted(new_perms.difference(self.existing_perms)),
                "removed": sorted(self.existing_perms.difference(new_perms)),
            }
        return change_message


@admin.register(account_models.UserGroup)
class UserGroupAdmin(GetManyFromRemoteMixin, HOPEModelAdminBase):
    list_display = ("user", "group", "business_area")
    autocomplete_fields = ("group",)
    raw_id_fields = ("user", "business_area", "group")
    search_fields = ("user__username__istartswith",)
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("group", AutoCompleteFilter),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "business_area",
                "user",
                "group",
            )
        )

    def check_sync_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.is_staff

    def check_publish_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False

    def _get_data(self, record: Any) -> str:
        groups = Group.objects.all()
        collector = ForeignKeysCollector(None)
        objs = []
        for qs in [groups]:
            objs.extend(qs)
        objs.extend(account_models.UserGroup.objects.filter(pk=record.pk))
        collector.collect(objs)
        serializer = self.get_serializer("json")
        return serializer.serialize(
            collector.data, use_natural_foreign_keys=True, use_natural_primary_keys=True, indent=3
        )
