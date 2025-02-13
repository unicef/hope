import logging
from typing import Any, Dict, Optional

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from adminactions.export import ForeignKeysCollector
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.combo import AllValuesComboFilter

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.admin.forms import (
    UserRoleAdminForm,
    UserRoleInlineFormSet,
)
from hct_mis_api.apps.account.models import Role
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

logger = logging.getLogger(__name__)


class UserRoleInline(admin.TabularInline):
    model = account_models.UserRole
    extra = 0
    formset = UserRoleInlineFormSet
    raw_id_fields = ("business_area", "role")


@admin.register(account_models.UserRole)
class UserRoleAdmin(HOPEModelAdminBase):
    list_display = ("user", "role", "business_area", "expiry_date")
    form = UserRoleAdminForm
    autocomplete_fields = ("role",)
    raw_id_fields = ("user", "business_area", "role")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
        ("role__subsystem", AllValuesComboFilter),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "business_area",
                "user",
                "role",
            )
        )

    def get_actions(self, request: HttpRequest) -> Dict:
        return admin.ModelAdmin.get_actions(self, request)  # unoverride

    def check_sync_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return request.user.is_staff

    def check_publish_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    def _get_data(self, record: Any) -> str:
        roles = Role.objects.all()
        collector = ForeignKeysCollector(None)
        objs = []
        for qs in [roles]:
            objs.extend(qs)
        objs.extend(account_models.UserRole.objects.filter(pk=record.pk))
        collector.collect(objs)
        serializer = self.get_serializer("json")
        return serializer.serialize(
            collector.data, use_natural_foreign_keys=True, use_natural_primary_keys=True, indent=3
        )
