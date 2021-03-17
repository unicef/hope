from admin_extra_urls.api import ExtraUrlMixin, action
from adminfilters.filters import ChoicesFieldComboFilter, RelatedFieldComboFilter, TextFieldFilter
from django import forms
from django.contrib import admin, messages

from django.core.validators import MinValueValidator
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.models import TargetPopulation, HouseholdSelection
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class RuleTestForm(forms.Form):
    rule = forms.ModelChoiceField(queryset=Rule.objects.all())
    number_of_records = forms.IntegerField(validators=[MinValueValidator(1)])


@admin.register(TargetPopulation)
class TargetPopulationAdmin(ExtraUrlMixin, HOPEModelAdminBase):
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
        ("business_area", RelatedFieldComboFilter),
        "is_removed",
        "sent_to_datahub",
    )
    raw_id_fields = (
        "created_by",
        "approved_by",
        "finalized_by",
        "business_area",
        "program",
        "final_list_targeting_criteria",
        "candidate_list_targeting_criteria",
    )

    @action()
    def selection(self, request, pk):
        obj = self.get_object(request, pk)
        url = reverse("admin:targeting_householdselection_changelist")
        return HttpResponseRedirect(f"{url}?target_population|id={obj.id}")

    @action()
    def test_steficon(self, request, pk):
        context = self.get_common_context(request, pk)
        if request.method == "GET":
            context["title"] = f"Test Steficon rule"
            context["form"] = RuleTestForm(initial={"number_of_records": 100, "rule": self.object.steficon_rule})
        else:
            form = RuleTestForm(request.POST)
            if form.is_valid():
                rule = form.cleaned_data["rule"]
                records = form.cleaned_data["number_of_records"]
                context["title"] = f"Test results of `{rule.name}` against `{self.object}`"
                context["target_population"] = self.object
                context["rule"] = rule
                elements = []
                context["elements"] = elements
                entries = self.object.selections.all()[:records]
                if entries:
                    for tp in entries:
                        value = context["rule"].execute(hh=tp.household)
                        tp.vulnerability_score = value
                        elements.append(tp)
                    self.message_user(request, "%s scores calculated" % len(elements))
                else:
                    self.message_user(request, "No records found", messages.WARNING)
        return TemplateResponse(request, "admin/targeting/steficon.html", context)


@admin.register(HouseholdSelection)
class HouseholdSelectionAdmin(HOPEModelAdminBase):
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
    )
