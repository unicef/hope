import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from django.contrib import admin
from django.contrib.admin.utils import construct_change_message
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_buttons.decorators import button
from admin_sync.collector import ForeignKeysCollector
from admin_sync.mixin import SyncMixin
from admin_sync.protocol import LoadDumpProtocol
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.admin.filters import (
    IncompatibleRoleFilter,
    PermissionFilter,
)
from hct_mis_api.apps.account.admin.forms import RoleAdminForm
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

logger = logging.getLogger(__name__)


class RoleResource(resources.ModelResource):
    class Meta:
        model = account_models.Role
        fields = ("name", "subsystem", "permissions")
        import_id_fields = ("name", "subsystem")


class UnrelatedForeignKeysCollector(ForeignKeysCollector):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(False)


class UnrelatedForeignKeysProtocol(LoadDumpProtocol):
    collector_class = UnrelatedForeignKeysCollector


@admin.register(account_models.Role)
class RoleAdmin(ImportExportModelAdmin, SyncMixin, HOPEModelAdminBase):
    list_display = ("name", "subsystem")
    search_fields = ("name",)
    form = RoleAdminForm
    list_filter = (PermissionFilter, "subsystem")
    resource_class = RoleResource
    change_list_template = "admin/account/role/change_list.html"
    protocol_class = UnrelatedForeignKeysProtocol

    @button()
    def members(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:
        url = reverse("admin:account_userrole_changelist")
        return HttpResponseRedirect(f"{url}?role__id__exact={pk}")

    @button()
    def matrix(self, request: HttpRequest) -> TemplateResponse:
        ctx = self.get_common_context(request, action="Matrix")
        matrix1 = {}
        matrix2 = {}
        perms = sorted(str(x.value) for x in Permissions)
        roles = account_models.Role.objects.order_by("name").filter(subsystem="HOPE")
        for perm in perms:
            granted_to_roles = []
            for role in roles:
                if role.permissions and perm in role.permissions:
                    granted_to_roles.append("X")
                else:
                    granted_to_roles.append("")
            matrix1[perm] = granted_to_roles

        for role in roles:
            values = []
            for perm in perms:
                if role.permissions and perm in role.permissions:
                    values.append("X")
                else:
                    values.append("")
            matrix2[role.name] = values

        ctx["permissions"] = perms
        ctx["roles"] = roles.values_list("name", flat=True)
        ctx["matrix1"] = matrix1
        ctx["matrix2"] = matrix2
        return TemplateResponse(request, "admin/account/role/matrix.html", ctx)

    def _perms(self, request: HttpRequest, object_id: str) -> set:
        return set(self.get_object(request, object_id).permissions or [])

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: Optional[str] = None,
        form_url: str = "",
        extra_context: Optional[Dict] = None,
    ) -> HttpResponse:
        if object_id:
            self.existing_perms = self._perms(request, object_id)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def construct_change_message(self, request: HttpRequest, form: Any, formsets: Any, add: bool = False) -> List[Dict]:
        change_message = construct_change_message(form, formsets, add)
        if not add and "permissions" in form.changed_data:
            new_perms = self._perms(request, form.instance.id)
            changed: Dict[str, Any] = change_message[0]["changed"]
            changed["permissions"] = {
                "added": sorted(new_perms.difference(self.existing_perms)),
                "removed": sorted(self.existing_perms.difference(new_perms)),
            }
        return change_message


@admin.register(account_models.IncompatibleRoles)
class IncompatibleRolesAdmin(HOPEModelAdminBase):
    list_display = ("role_one", "role_two")
    list_filter = (IncompatibleRoleFilter,)
