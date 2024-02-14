from typing import Optional

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter

from hct_mis_api.apps.household.forms import CreateTargetPopulationTextForm
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.targeting.celery_tasks import create_tp_from_list
from hct_mis_api.apps.targeting.models import TargetingCriteria
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)


@admin.register(ProgramCycle)
class ProgramCycleAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("program", "iteration", "status", "start_date", "end_date")
    date_hierarchy = "program__start_date"
    list_filter = (("status", ChoicesFieldComboFilter),)
    raw_id_fields = ("program",)


class ProgramCycleAdminInline(admin.TabularInline):
    model = ProgramCycle
    extra = 0
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Program)
class ProgramAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("name", "status", "start_date", "end_date", "business_area", "data_collecting_type")
    date_hierarchy = "start_date"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("scope", ChoicesFieldComboFilter),
        "is_visible",
    )
    raw_id_fields = ("business_area",)
    filter_horizontal = ("admin_areas",)

    inlines = (ProgramCycleAdminInline,)
    ordering = ("name",)

    @button(
        permission="targeting.add_targetpopulation",
    )
    def create_target_population_from_list(self, request: HttpRequest, pk: str) -> Optional[HttpResponse]:
        context = self.get_common_context(request, title="Create TargetPopulation")
        program = Program.objects.get(pk=pk)
        business_area = program.business_area

        if "apply" in request.POST:
            form = CreateTargetPopulationTextForm(request.POST, read_only=True, program=program)
            if request.POST["criteria"] and form.is_valid():
                context["ba_name"] = business_area.name
                context["programme_name"] = program.name
                context["total"] = len(form.cleaned_data["criteria"])

        elif "confirm" in request.POST:
            create_tp_from_list.delay(request.POST.dict(), request.user.pk, program.pk)
            message = mark_safe(f'Creation of target population <b>{request.POST["name"]}</b> scheduled.')
            messages.success(request, message)
            url = reverse("admin:targeting_targetpopulation_changelist")
            return HttpResponseRedirect(url)

        else:
            targeting_criteria = TargetingCriteria()
            targeting_criteria.save()
            form = CreateTargetPopulationTextForm(
                initial={"action": "create_tp_from_list", "targeting_criteria": targeting_criteria}, program=program
            )

        context["form"] = form
        return TemplateResponse(request, "admin/program/program/create_target_population_from_text.html", context)
