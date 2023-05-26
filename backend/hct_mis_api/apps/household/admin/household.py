import logging
from itertools import chain
from typing import Any, List, Optional
from uuid import UUID

from django.contrib import admin, messages
from django.contrib.messages import DEFAULT_TAGS
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.querystring import QueryStringFilter
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.power_query.mixin import PowerQueryMixin
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)

from hct_mis_api.apps.utils.security import is_root
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Household,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.household.admin.mixins import CustomTargetPopulationMixin, HouseholdWithDrawnMixin

logger = logging.getLogger(__name__)


@admin.register(Household)
class HouseholdAdmin(
    SoftDeletableAdminMixin,
    LastSyncDateResetMixin,
    LinkedObjectsMixin,
    PowerQueryMixin,
    SmartFieldsetMixin,
    CursorPaginatorAdmin,
    HouseholdWithDrawnMixin,
    CustomTargetPopulationMixin,
    HOPEModelAdminBase,
):
    list_display = (
        "unicef_id",
        "business_area",
        "country",
        "head_of_household",
        "size",
        "withdrawn",
    )
    list_filter = (
        DepotManager,
        ("business_area", AutoCompleteFilter),
        QueryStringFilter,
        "withdrawn",
    )
    search_fields = ("head_of_household__family_name", "unicef_id")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("representatives", "programs")
    raw_id_fields = (
        "admin_area",
        "business_area",
        "country",
        "country_origin",
        "currency",
        "head_of_household",
        "registration_data_import",
    )
    fieldsets = [
        (None, {"fields": (("unicef_id", "head_of_household"),)}),
        (
            "Registration",
            {
                "classes": ("collapse",),
                "fields": (
                    "registration_data_import",
                    "registration_method",
                    "first_registration_date",
                    "last_registration_date",
                    "org_enumerator",
                    "org_name_enumerator",
                    "name_enumerator",
                ),
            },
        ),
        (
            "Dates",
            {
                "classes": ("collapse",),
                "fields": (
                    ("created_at", "updated_at"),
                    "last_sync_at",
                    "removed_date",
                    "withdrawn_date",
                ),
            },
        ),
        ("Others", {"classes": ("collapse",), "fields": ("__others__",)}),
    ]
    actions = [
        "mass_withdraw",
        "mass_unwithdraw",
        "count_queryset",
        "create_target_population",
        "add_to_target_population",
    ]
    cursor_ordering_field = "unicef_id"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = self.model.all_objects.get_queryset().select_related(
            "head_of_household", "country", "country_origin", "admin_area"
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_ignored_linked_objects(self, request: HttpRequest) -> List:
        return []

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    @button()
    def tickets(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Tickets")
        obj = context["original"]
        tickets = []
        for entry in chain(obj.sensitive_ticket_details.all(), obj.complaint_ticket_details.all()):
            tickets.append(entry.ticket)
        context["tickets"] = tickets
        return TemplateResponse(request, "admin/household/household/tickets.html", context)

    @button()
    def members(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        obj = Household.objects.get(pk=pk)
        url = reverse("admin:household_individual_changelist")
        return HttpResponseRedirect(f"{url}?qs=unicef_id={obj.unicef_id}")

    @button()
    def sanity_check(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        # NOTE: this code is should be optimized in the future and it is not
        # intended to be used in bulk
        hh = self.get_object(request, str(pk))
        warnings: List[List] = []
        primary = None
        head = None
        try:
            primary = IndividualRoleInHousehold.objects.get(household=hh, role=ROLE_PRIMARY)
        except ObjectDoesNotExist:
            warnings.append([messages.ERROR, "Head of househould not found"])

        alternate = IndividualRoleInHousehold.objects.filter(household=hh, role=ROLE_ALTERNATE).first()
        try:
            head = hh.individuals.get(relationship=HEAD)
        except ObjectDoesNotExist:
            warnings.append([messages.ERROR, "Head of househould not found"])

        total_in_ranges = 0
        for gender in ["male", "female"]:
            for num_range in ["0_5", "6_11", "12_17", "18_59", "60"]:
                field = f"{gender}_age_group_{num_range}_count"
                total_in_ranges += getattr(hh, field, 0) or 0

        active_individuals = hh.individuals.exclude(Q(duplicate=True) | Q(withdrawn=True))
        ghosts_individuals = hh.individuals.filter(Q(duplicate=True) | Q(withdrawn=True))
        all_individuals = hh.individuals.all()
        if hh.collect_individual_data:
            if active_individuals.count() != hh.size:
                warnings.append([messages.WARNING, "HH size does not match"])

        else:
            if all_individuals.count() > 1:
                warnings.append([messages.ERROR, "Individual data not collected but members found"])

        if hh.size != total_in_ranges:
            warnings.append(
                [
                    messages.ERROR,
                    f"HH size ({hh.size}) and ranges population ({total_in_ranges}) does not match",
                ]
            )

        aaaa = active_individuals.values_list("unicef_id", flat=True)
        bbb = Household.objects.filter(unicef_id__in=aaaa)
        if bbb.count() > len(aaaa):
            warnings.append([messages.ERROR, "Unmarked duplicates found"])

        context = {
            "active_individuals": active_individuals,
            "ghosts_individuals": ghosts_individuals,
            "opts": Household._meta,
            "app_label": Household._meta.app_label,
            "original": hh,
            "head": head,
            "primary": primary,
            "alternate": alternate,
            "warnings": [(DEFAULT_TAGS[w[0]], w[1]) for w in warnings],
        }
        return TemplateResponse(request, "admin/household/household/sanity_check.html", context)

    @button(permission=lambda request, obj, handler: is_root(request, obj, handler) and obj.can_be_erase())
    def gdpr_remove(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        household: Household = self.get_queryset(request).get(pk=pk)
        if request.method == "POST":
            try:
                with transaction.atomic():
                    household.erase()
                self.message_user(request, f"Household {household.unicef_id} erased.", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:household_household_change", args=[pk]))
        return confirm_action(
            self,
            request,
            self.gdpr_remove,
            mark_safe(
                """<h1>Household erase</h1>
                <p>After this operation household will be erased, all sensitive data will be overwritten.</p>
                <p>This operation cannot be undo.</p>
                """
            ),
            "Successfully executed",
        )

    @button(permission=lambda request, household, *args, **kwargs: is_root(request) and not household.is_removed)
    def logical_delete(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        household: Household = self.get_queryset(request).get(pk=pk)
        if request.method == "POST":
            try:
                household.delete()
                self.message_user(request, f"Household {household.unicef_id} was soft removed.", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:household_household_change", args=[pk]))
        return confirm_action(
            self,
            request,
            self.logical_delete,
            mark_safe(
                """<h1>Household logical delete</h1>
                <p>After this operation household will be marked as logical deleted and will be hidden in the application.</p>
                """
            ),
            "Successfully executed",
        )
