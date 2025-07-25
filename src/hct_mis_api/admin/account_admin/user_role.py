import logging
from typing import Any, Dict, Optional

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.combo import AllValuesComboFilter

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.admin.account_admin.forms import (
    RoleAssignmentAdminForm,
    RoleAssignmentInlineFormSet,
)
from hct_mis_api.apps.account.models import Partner, Role
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

logger = logging.getLogger(__name__)


class RoleAssignmentInline(admin.TabularInline):
    model = account_models.RoleAssignment
    fields = ["business_area", "program", "role", "expiry_date"]
    extra = 0
    formset = RoleAssignmentInlineFormSet

    def formfield_for_foreignkey(self, db_field: Any, request: Any = None, **kwargs: Any) -> Any:
        partner_id = request.resolver_match.kwargs.get("object_id")

        if db_field.name == "business_area":
            if partner_id and partner_id.isdigit():
                partner = Partner.objects.get(id=partner_id)
                kwargs["queryset"] = BusinessArea.objects.filter(
                    id__in=partner.allowed_business_areas.all().values("id"),
                    is_split=False,
                )
            else:
                kwargs["queryset"] = BusinessArea.objects.filter(is_split=False)

        elif db_field.name == "role":
            if partner_id and partner_id.isdigit():
                kwargs["queryset"] = Role.objects.filter(
                    is_available_for_partner=True,
                )
            else:
                kwargs["queryset"] = Role.objects.all()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        if isinstance(obj, Partner):
            if obj.is_parent or obj.is_unicef_subpartner:
                return False  # Disable adding if Partner is a parent or is a UNICEF subpartner
            return request.user.can_add_business_area_to_partner()
        return True

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        if isinstance(obj, Partner):
            if obj.is_unicef_subpartner:
                return False  # Disable editing if Partner is a UNICEF subpartner
            return request.user.can_add_business_area_to_partner()
        return True

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        if isinstance(obj, Partner):
            if obj.is_unicef_subpartner:
                return False  # Disable deleting if Partner is a UNICEF subpartner
            return request.user.can_add_business_area_to_partner()
        return True


@admin.register(account_models.RoleAssignment)
class RoleAssignmentAdmin(HOPEModelAdminBase):
    list_display = ("user", "partner", "role", "business_area", "program")
    form = RoleAssignmentAdminForm
    autocomplete_fields = ("role",)
    raw_id_fields = ("user", "business_area", "role")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
        ("role__subsystem", AllValuesComboFilter),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "business_area",
                "program",
                "user",
                "partner",
                "role",
            )
        )

    def get_actions(self, request: HttpRequest) -> Dict:
        return admin.ModelAdmin.get_actions(self, request)  # unoverride

    def check_sync_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.is_staff

    def check_publish_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False
