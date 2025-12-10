import logging
from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.combo import AllValuesComboFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from hope.admin.account_forms import (
    RoleAssignmentAdminForm,
    RoleAssignmentInlineFormSet,
)
from hope.admin.utils import HOPEModelAdminBase
from hope.apps.account import models as account_models
from hope.apps.account.models import Partner, Role
from hope.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


class RoleAssignmentInline(admin.TabularInline):
    model = account_models.RoleAssignment
    fields = ["business_area", "program", "role", "expiry_date"]
    extra = 0
    formset = RoleAssignmentInlineFormSet
    ordering = ["business_area__name"]

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

    def has_add_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        if isinstance(obj, Partner):
            if obj.is_parent:
                return False
            return request.user.can_add_business_area_to_partner()
        return True

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        if isinstance(obj, Partner):
            return request.user.can_add_business_area_to_partner()
        return True

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        if isinstance(obj, Partner):
            return request.user.can_add_business_area_to_partner()
        return True


class BaseRoleAssignmentAdmin(HOPEModelAdminBase):
    form = RoleAssignmentAdminForm

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

    def formfield_for_foreignkey(self, db_field: Any, request: Any = None, **kwargs: Any) -> Any:
        if db_field.name == "role":
            kwargs["queryset"] = Role.objects.order_by("name")
        elif db_field.name == "business_area":
            kwargs["queryset"] = BusinessArea.objects.filter(is_split=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_actions(self, request: HttpRequest) -> dict:
        return admin.ModelAdmin.get_actions(self, request)  # unoverride

    def check_sync_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.is_staff

    def check_publish_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False


@admin.register(account_models.UserRoleAssignment)
class UserRoleAssignmentAdmin(BaseRoleAssignmentAdmin):
    list_display = ("user", "role", "business_area", "program")
    autocomplete_fields = ("user", "business_area", "role", "program", "group")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )
    list_filter = (
        ("user", AutoCompleteFilter),
        ("business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
        ("role__subsystem", AllValuesComboFilter),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.filter(user__isnull=False)

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.has_perm("account.can_edit_user_roles")

    def has_view_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.has_perm("account.can_edit_user_roles")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.has_perm("account.can_edit_user_roles")

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.has_perm("account.can_edit_user_roles")

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.has_perm("account.can_edit_user_roles")

    def get_fields(self, request: HttpRequest, obj: Any | None = None) -> list:
        return ["user", "business_area", "program", "role", "expiry_date", "group"]


@admin.register(account_models.PartnerRoleAssignment)
class PartnerRoleAssignmentAdmin(BaseRoleAssignmentAdmin):
    list_display = ("partner", "role", "business_area", "program")
    autocomplete_fields = ("partner", "business_area", "role", "program", "group")
    search_fields = ("partner__name",)
    list_filter = (
        ("partner", AutoCompleteFilter),
        ("business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
        ("role__subsystem", AllValuesComboFilter),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.filter(partner__isnull=False)

    def get_fields(self, request: HttpRequest, obj: Any | None = None) -> list:
        return ["partner", "business_area", "program", "role", "expiry_date", "group"]

    def formfield_for_foreignkey(self, db_field: Any, request: Any = None, **kwargs: Any) -> Any:
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "role":
            field.queryset = Role.objects.filter(is_available_for_partner=True).order_by("name")
        return field
