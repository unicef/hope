from typing import Optional

from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_buttons.decorators import button

from hct_mis_api.apps.household.forms import CreateTargetPopulationTextForm
from hct_mis_api.apps.targeting.models import TargetingCriteria, TargetPopulation
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import refresh_stats


class TargetPopulationFromListMixin:
    @button()
    def create_target_population_from_list(self, request: HttpRequest) -> Optional[HttpResponse]:
        context = self.get_common_context(request, title="Create TargetPopulation")
        if "apply" in request.POST:
            form = CreateTargetPopulationTextForm(request.POST, read_only=True)
            if form.is_valid():
                context["ba_name"] = form.cleaned_data["business_area"].name
                context["households"] = form.cleaned_data["criteria"][:101]
                context["total"] = form.cleaned_data["criteria"].count()
        elif "confirm" in request.POST:
            form = CreateTargetPopulationTextForm(request.POST)
            if form.is_valid():
                ba = form.cleaned_data["business_area"]
                population = form.cleaned_data["criteria"]
                with atomic():
                    tp = TargetPopulation.objects.create(
                        targeting_criteria=form.cleaned_data["targeting_criteria"],
                        created_by=request.user,
                        name=form.cleaned_data["name"],
                        business_area=ba,
                    )
                    tp.households.set(population)
                    refresh_stats(tp)
                    tp.save()
                url = reverse("admin:targeting_targetpopulation_change", args=[tp.pk])
                return HttpResponseRedirect(url)
        else:
            targeting_criteria = TargetingCriteria()
            targeting_criteria.save()
            form = CreateTargetPopulationTextForm(
                initial={"action": "create_tp_from_list", "targeting_criteria": targeting_criteria}
            )
        context["form"] = form
        return TemplateResponse(request, "admin/household/household/create_target_population_from_text.html", context)
