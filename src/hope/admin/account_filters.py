import logging
from typing import Any, Iterable

from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.http import HttpRequest

from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Role

logger = logging.getLogger(__name__)


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
        types = Role.objects.values_list("id", "name")
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
