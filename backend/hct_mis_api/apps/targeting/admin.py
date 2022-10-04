from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, MaxMinFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.targeting.celery_tasks import target_population_apply_steficon
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, SoftDeletableAdminMixin

from .models import HouseholdSelection, TargetPopulation
from .steficon import SteficonExecutorMixin


@admin.register(TargetPopulation)
class TargetPopulationAdmin(
    SoftDeletableAdminMixin, SteficonExecutorMixin, LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase
):
    list_display = (
        "name",
        "status",
        "sent_to_datahub",
        "business_area",
        "program",
        # "candidate_list_total_households",
        # "candidate_list_total_individuals",
        # "final_list_total_households",
        # "final_list_total_individuals",
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
    def selection(self, request, pk):
        obj = self.get_object(request, pk)
        url = reverse("admin:targeting_householdselection_changelist")
        return HttpResponseRedirect(f"{url}?target_population={obj.id}")

    @button()
    def inspect(self, request, pk):
        context = self.get_common_context(request, pk, aeu_groups=[None], action="Inspect")

        return TemplateResponse(request, "admin/targeting/targetpopulation/inspect.html", context)

    @button()
    def payments(self, request, pk):
        context = self.get_common_context(request, pk, aeu_groups=[None], action="payments")

        return TemplateResponse(request, "admin/targeting/targetpopulation/payments.html", context)

    # @button()
    # def download_xlsx(self, request, pk):
    #     return redirect("admin-download-target-population", target_population_id=pk)

    @button()
    def rerun_steficon(self, request, pk):
        def _rerun(request):
            context = self.get_common_context(request, pk)
            target_population_apply_steficon.delay(pk)
            return TemplateResponse(request, "admin/targeting/targetpopulation/rule_change.html", context)

        return confirm_action(
            self,
            request,
            _rerun,
            "Do you want to rerun the steficon rule ?",
            "Updating target population in the background with correct scores.",
        )


@admin.register(HouseholdSelection)
class HouseholdSelectionAdmin(ExtraButtonsMixin, HOPEModelAdminBase):
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

    def reset_sync_date(self, request, queryset):
        from hct_mis_api.apps.household.models import Household

        Household.objects.filter(selections__in=queryset).update(last_sync_at=None)

    def reset_vulnerability_score(self, request, queryset):
        queryset.update(vulnerability_score=None)
