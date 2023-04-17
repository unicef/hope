from typing import Optional

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_buttons.decorators import button

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.forms import CreateTargetPopulationTextForm
from hct_mis_api.apps.targeting.celery_tasks import create_tp_from_list
from hct_mis_api.apps.targeting.models import TargetingCriteria


class TargetPopulationFromListMixin:
    @button()
    def create_target_population_from_list(self, request: HttpRequest) -> Optional[HttpResponse]:
        context = self.get_common_context(request, title="Create TargetPopulation")
        if "apply" in request.POST:
            form = CreateTargetPopulationTextForm(request.POST, read_only=True)
            if request.POST["criteria"]:
                context["ba_name"] = BusinessArea.objects.get(pk=request.POST["business_area"]).name
        elif "confirm" in request.POST:
            form = CreateTargetPopulationTextForm(request.POST)
            create_tp_from_list.delay(request.POST.dict(), request.user.pk)
            message = mark_safe(
                f'Creation of target population <b>{request.POST["name"]}</b> scheduled.\
                Please check in a moment and update its program.'
            )
            messages.success(request, message)
            url = reverse("admin:targeting_targetpopulation_changelist")
            return HttpResponseRedirect(url)
        else:
            targeting_criteria = TargetingCriteria()
            targeting_criteria.save()
            form = CreateTargetPopulationTextForm(
                initial={"action": "create_tp_from_list", "targeting_criteria": targeting_criteria}
            )
        context["form"] = form
        return TemplateResponse(request, "admin/household/household/create_target_population_from_text.html", context)
