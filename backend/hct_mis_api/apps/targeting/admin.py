from typing import Optional
from uuid import UUID

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_buttons.api import button, confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, MaxMinFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.targeting.celery_tasks import target_population_apply_steficon
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, SoftDeletableAdminMixin

from hct_mis_api.apps.targeting.forms import TargetPopulationForm
from hct_mis_api.apps.targeting.mixins import TargetPopulationFromListMixin
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation
from hct_mis_api.apps.targeting.steficon import SteficonExecutorMixin


@admin.register(TargetPopulation)
class TargetPopulationAdmin(
    SoftDeletableAdminMixin,
    SteficonExecutorMixin,
    TargetPopulationFromListMixin,
    LinkedObjectsMixin,
    HOPEModelAdminBase,
):
    form = TargetPopulationForm
    list_display = (
        "name",
        "status",
        "sent_to_datahub",
        "business_area",
        "program",
    )
    date_hierarchy = "created_at"
    search_fields = ("name",)
    list_filter = (
        DepotManager,
        QueryStringFilter,
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("steficon_rule__rule", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        "sent_to_datahub",
    )
    raw_id_fields = (
        "created_by",
        "changed_by",
        "finalized_by",
        "business_area",
        "program",
        "targeting_criteria",
    )

    @button()
    def selection(self, request: "HttpRequest", pk: "UUID") -> "HttpResponse":
        obj = self.get_object(request, str(pk))
        url = reverse("admin:targeting_householdselection_changelist")
        return HttpResponseRedirect(f"{url}?target_population={obj.id}")

    @button()
    def inspect(self, request: "HttpRequest", pk: "UUID") -> TemplateResponse:
        context = self.get_common_context(request, pk, aeu_groups=[None], action="Inspect")

        return TemplateResponse(request, "admin/targeting/targetpopulation/inspect.html", context)

    @button()
    def payments(self, request: "HttpRequest", pk: "UUID") -> TemplateResponse:
        context = self.get_common_context(request, pk, aeu_groups=[None], action="payments")

        return TemplateResponse(request, "admin/targeting/targetpopulation/payments.html", context)

    @button(enabled=lambda b: b.context["original"].steficon_rule)
    def rerun_steficon(self, request: "HttpRequest", pk: "UUID") -> TemplateResponse:
        def _rerun(request: "HttpRequest") -> TemplateResponse:
            context = self.get_common_context(request, pk)
            target_population_apply_steficon.delay(pk)
            return TemplateResponse(request, "admin/targeting/targetpopulation/rule_change.html", context)

        obj: Optional[TargetPopulation] = self.get_object(request, str(pk))
        if not obj:
            raise Exception("Target population not found")
        return confirm_action(
            self,
            request,
            _rerun,
            "Do you want to rerun the steficon rule '%s' ?" % obj.steficon_rule,
            "Updating target population in the background with correct scores.",
            title="ddddd",
        )


@admin.register(HouseholdSelection)
class HouseholdSelectionAdmin(HOPEModelAdminBase):
    list_display = (
        "household",
        "target_population",
        "vulnerability_score",
    )
    raw_id_fields = (
        "household",
        "target_population",
    )
    list_filter = (
        DepotManager,
        QueryStringFilter,
        ("household__unicef_id", ValueFilter),
        ("target_population", AutoCompleteFilter),
        ("target_population__id", ValueFilter),
        ("vulnerability_score", MaxMinFilter),
    )
    actions = ["reset_sync_date", "reset_vulnerability_score"]

    def reset_sync_date(self, request: "HttpRequest", queryset: "QuerySet") -> None:
        from hct_mis_api.apps.household.models import Household

        Household.objects.filter(selections__in=queryset).update(last_sync_at=None)

    def reset_vulnerability_score(self, request: "HttpRequest", queryset: "QuerySet") -> None:
        queryset.update(vulnerability_score=None)
