from django import forms
from django.contrib import admin, messages
from django.core.validators import MinValueValidator
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_urls.api import ExtraUrlMixin, button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import (
    ChoicesFieldComboFilter,
    MaxMinFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, SoftDeletableAdminMixin


@admin.register(TargetPopulation)
class TargetPopulationAdmin(SoftDeletableAdminMixin, LinkedObjectsMixin, ExtraUrlMixin, HOPEModelAdminBase):
    list_display = (
        "name",
        "status",
        "candidate_list_total_households",
        "candidate_list_total_individuals",
        "final_list_total_households",
        "final_list_total_individuals",
    )
    search_fields = ("name",)
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        "sent_to_datahub",
    )
    raw_id_fields = (
        "created_by",
        "changed_by",
        "finalized_by",
        "business_area",
        "program",
        "final_list_targeting_criteria",
        "candidate_list_targeting_criteria",
    )

    @button()
    def selection(self, request, pk):
        obj = self.get_object(request, pk)
        url = reverse("admin:targeting_householdselection_changelist")
        return HttpResponseRedirect(f"{url}?target_population|id={obj.id}")

    @button()
    def inspect(self, request, pk):
        context = self.get_common_context(request, pk, aeu_groups=[None], action="Inspect")

        return TemplateResponse(request, "admin/targeting/targetpopulation/inspect.html", context)

    @button()
    def payments(self, request, pk):
        context = self.get_common_context(request, pk, aeu_groups=[None], action="payments")

        return TemplateResponse(request, "admin/targeting/targetpopulation/payments.html", context)

    # @button()
    # def test_steficon(self, request, pk):
    #     context = self.get_common_context(request, pk)
    #     if request.method == "GET":
    #         context["title"] = f"Test Steficon rule"
    #         context["form"] = RuleTestForm(initial={"number_of_records": 100, "rule": self.object.steficon_rule})
    #     else:
    #         form = RuleTestForm(request.POST)
    #         if form.is_valid():
    #             rule = form.cleaned_data["rule"]
    #             records = form.cleaned_data["number_of_records"]
    #             context["title"] = f"Test results of `{rule.name}` against `{self.object}`"
    #             context["target_population"] = self.object
    #             context["rule"] = rule
    #             elements = []
    #             context["elements"] = elements
    #             entries = self.object.selections.all()[:records]
    #             if entries:
    #                 for tp in entries:
    #                     value = context["rule"].execute(hh=tp.household)
    #                     tp.vulnerability_score = value
    #                     elements.append(tp)
    #                 self.message_user(request, "%s scores calculated" % len(elements))
    #             else:
    #                 self.message_user(request, "No records found", messages.WARNING)
    #     return TemplateResponse(request, "admin/targeting/steficon.html", context)


@admin.register(HouseholdSelection)
class HouseholdSelectionAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = (
        "household",
        "target_population",
        "vulnerability_score",
        "final",
    )
    raw_id_fields = (
        "household",
        "target_population",
    )
    list_filter = (
        TextFieldFilter.factory("household__unicef_id", "Household ID"),
        TextFieldFilter.factory("target_population__id", "Target Population ID"),
        "final",
        ("vulnerability_score", MaxMinFilter),
    )
    actions = ["reset_sync_date"]

    def reset_sync_date(self, request, queryset):
        from hct_mis_api.apps.household.models import Household

        Household.objects.filter(selections__in=queryset).update(last_sync_at=None)
