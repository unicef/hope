from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlencode

if TYPE_CHECKING:
    from django.contrib.admin.options import ActionLocation
    from django.db.models import QuerySet
    from django.db.models.fields.related import ForeignKey
    from django.forms import ModelChoiceField
    from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from hope.admin.account_forms import (
    RoleAssignmentAdminForm,
    RoleAssignmentInlineFormSet,
)
from hope.admin.utils import AutocompleteForeignKeyMixin, HOPEModelAdminBase
from hope.models import BusinessArea, Partner, PartnerRoleAssignment, Role, RoleAssignment, UserRoleAssignment

logger = logging.getLogger(__name__)


class PartnerAutocompleteSelect(AutocompleteSelect):
    """Autocomplete widget passing the edited partner id so the search can apply partner-scoped restrictions."""

    def __init__(self, field: ForeignKey, admin_site: admin.AdminSite, partner_id: str | None, **kwargs: Any) -> None:
        super().__init__(field, admin_site, **kwargs)
        self.partner_id = partner_id

    def get_url(self) -> str:
        return f"{super().get_url()}?{urlencode({'partner_id': self.partner_id or ''})}"


def is_autocomplete_for(request: HttpRequest, model_name: str, field_name: str) -> bool:
    return (
        "partner_id" in request.GET
        and request.GET.get("app_label") == "account"
        and request.GET.get("model_name") == model_name
        and request.GET.get("field_name") == field_name
    )


def get_autocomplete_partner(request: HttpRequest) -> Partner | None:
    partner_id = request.GET.get("partner_id", "")
    return Partner.objects.filter(id=partner_id).first() if partner_id.isdigit() else None


def limit_business_areas_for_partner(queryset: QuerySet, partner: Partner | None) -> QuerySet:
    queryset = queryset.filter(is_split=False)
    if partner:
        queryset = queryset.filter(id__in=partner.allowed_business_areas.all().values("id"))
    return queryset


def limit_roles_for_partner(queryset: QuerySet, partner: Partner | None) -> QuerySet:
    if partner and not partner.is_unicef_subpartner:
        return queryset.filter(is_available_for_partner=True)
    return queryset


class RoleAssignmentInline(AutocompleteForeignKeyMixin, admin.TabularInline):
    model = RoleAssignment
    fields = ["business_area", "program", "role", "expiry_date"]
    extra = 0
    formset = RoleAssignmentInlineFormSet
    ordering = ["business_area__name"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("business_area", "role", "user", "partner__parent")

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs: Any
    ) -> ModelChoiceField | None:
        if db_field.name in ("business_area", "role"):
            partner_id = request.resolver_match.kwargs.get("object_id")
            if not (partner_id and partner_id.isdigit()):
                partner_id = None
            partner = Partner.objects.get(id=partner_id) if partner_id else None
            if db_field.name == "business_area":
                kwargs["queryset"] = limit_business_areas_for_partner(BusinessArea.objects.all(), partner)
            else:
                kwargs["queryset"] = limit_roles_for_partner(Role.objects.all(), partner)
            kwargs["widget"] = PartnerAutocompleteSelect(db_field, self.admin_site, partner_id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BaseRoleAssignmentAdmin(HOPEModelAdminBase):
    form = RoleAssignmentAdminForm
    # business_area is restricted to is_split=False via formfield_for_foreignkey;
    # the autocomplete widget bypasses that queryset, so it must be excluded.
    autocomplete_exclude_fields: tuple[str, ...] = ("business_area",)

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

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs: Any
    ) -> ModelChoiceField | None:
        if db_field.name == "role":
            kwargs["queryset"] = Role.objects.order_by("name")
        elif db_field.name == "business_area":
            kwargs["queryset"] = BusinessArea.objects.filter(is_split=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_actions(self, request: HttpRequest, action_location: ActionLocation | None = None) -> dict:
        return admin.ModelAdmin.get_actions(self, request)  # unoverride

    def check_sync_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.is_staff

    def check_publish_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(BaseRoleAssignmentAdmin):
    list_display = ("user", "role", "business_area", "program")
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
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.filter(user__isnull=False)

    def get_fields(self, request: HttpRequest, obj: Any | None = None) -> list:
        return ["user", "business_area", "program", "role", "expiry_date", "group"]


@admin.register(PartnerRoleAssignment)
class PartnerRoleAssignmentAdmin(BaseRoleAssignmentAdmin):
    list_display = ("partner", "role", "business_area", "program")
    search_fields = ("partner__name",)
    list_filter = (
        ("partner", AutoCompleteFilter),
        ("business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
    )
    # role is restricted to is_available_for_partner=True via formfield_for_foreignkey;
    # the autocomplete widget bypasses that queryset, so it must be excluded.
    autocomplete_exclude_fields = ("business_area", "role")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.filter(partner__isnull=False)

    def get_fields(self, request: HttpRequest, obj: Any | None = None) -> list:
        return ["partner", "business_area", "program", "role", "expiry_date", "group"]

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs: Any
    ) -> ModelChoiceField | None:
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "role":
            object_id = request.resolver_match.kwargs.get("object_id")
            obj = self.get_object(request, cast("str", object_id)) if object_id else None
            if obj and obj.partner and obj.partner.is_unicef_subpartner:
                field.queryset = Role.objects.order_by("name")
            else:
                field.queryset = Role.objects.filter(is_available_for_partner=True).order_by("name")
        return field
