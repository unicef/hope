import logging
from typing import Any, Iterable

from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.http import HttpRequest

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


class HasKoboAccount(SimpleListFilter):
    parameter_name = "kobo_account"
    title = "Has Kobo Access"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> tuple:
        return (1, "Yes"), (0, "No")

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() == "0":
            return queryset.filter(Q(custom_fields__kobo_pk__isnull=True) | Q(custom_fields__kobo_pk=None))
        if self.value() == "1":
            return queryset.filter(custom_fields__kobo_pk__isnull=False).exclude(custom_fields__kobo_pk=None)
        return queryset


class BusinessAreaFilter(SimpleListFilter):
    parameter_name = "ba"
    title = "Business Area"
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[Any]") -> list:
        return BusinessArea.objects.filter(role_assignments__user__isnull=False).values_list("id", "name").distinct()

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        return queryset.filter(role_assignments__business_area=self.value()).distinct() if self.value() else queryset


class PermissionFilter(SimpleListFilter):
    title = "Permission Name"
    parameter_name = "perm"
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[Any]") -> Iterable[tuple[Any, str]] | None:
        return Permissions.choices()

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if not self.value():
            return queryset
        return queryset.filter(permissions__contains=[self.value()])


class IncompatibleRoleFilter(SimpleListFilter):
    template = "adminfilters/combobox.html"
    title = "Role"
    parameter_name = "role"

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[Any]") -> list:
        types = account_models.Role.objects.values_list("id", "name")
        return list(types.order_by("name").distinct())

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if not self.value():
            return queryset
        try:
            return queryset.filter(
                Q(role_one=self.value()) | Q(role_two=self.value()),
            )
        except (ValueError, ValidationError) as e:
            logger.warning(e)
            raise IncorrectLookupParameters(e)
