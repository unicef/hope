from typing import Any, Optional, Union

from django import forms
from django.contrib import admin, messages
from django.db.models import Q, QuerySet
from django.forms import CheckboxSelectMultiple, formset_factory
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.forms import CreateTargetPopulationTextForm
from hct_mis_api.apps.program.models import Program, ProgramCycle, ProgramPartnerThrough
from hct_mis_api.apps.targeting.celery_tasks import create_tp_from_list
from hct_mis_api.apps.targeting.models import TargetingCriteria
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from mptt.forms import TreeNodeMultipleChoiceField


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


class PartnerAreaForm(forms.Form):
    partner = forms.ModelChoiceField(queryset=Partner.objects.all(), required=True)
    # def __init__(self, *args: Any, **kwargs: Any) -> None:
    #     self.business_area_id = kwargs.pop("business_area_id")
    #     super().__init__(*args, **kwargs)
    #
    #     self.fields["partner"] = forms.ModelChoiceField(queryset=self.get_partner_queryset())
    #
    # def get_partner_queryset(self) -> QuerySet[Partner]:
    #     return Partner.objects.filter(allowed_business_areas__id=self.business_area_id)
    # program = forms.ModelChoiceField(queryset=Program.objects.all(), required=True)
    areas = TreeNodeMultipleChoiceField(queryset=Area.objects.all(), widget=CheckboxSelectMultiple(), required=False)


@admin.register(Program)
class ProgramAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, AdminAutoCompleteSearchMixin, HOPEModelAdminBase):
    list_display = ("name", "status", "start_date", "end_date", "business_area", "data_collecting_type")
    date_hierarchy = "start_date"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("scope", ChoicesFieldComboFilter),
        "is_visible",
    )
    search_fields = ("name",)
    raw_id_fields = ("business_area",)
    filter_horizontal = ("admin_areas",)

    inlines = (ProgramCycleAdminInline,)
    ordering = ("name",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Program]:
        return super().get_queryset(request).select_related("data_collecting_type", "business_area")

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

    @button()
    def partners(self, request: HttpRequest, pk: int) -> Union[TemplateResponse, HttpResponseRedirect]:
        context = self.get_common_context(request, pk, title="Partner access")
        program: Program = context["original"]
        PartnerAreaFormSet = formset_factory(PartnerAreaForm, extra=0, can_delete=True)

        is_editable = program.partner_access != Program.SELECTED_PARTNERS_ACCESS

        if request.method == "GET" or not is_editable:
            partner_area_data = []
            for partner_program_through in program.program_partner_through.all():
                partner_area_data.append(
                    {
                        "partner": partner_program_through.partner,
                        "areas": [
                            str(area_id) for area_id in partner_program_through.areas.values_list("id", flat=True)
                        ],
                    }
                )
            partner_area_form_set = PartnerAreaFormSet(initial=partner_area_data, prefix="program_areas")
        elif request.method == "POST":
            partner_area_form_set = PartnerAreaFormSet(request.POST or None, prefix="program_areas")
            if partner_area_form_set.is_valid():
                for form in partner_area_form_set:
                    form = form.cleaned_data
                    if form and not form["DELETE"]:
                        areas_ids = list(map(lambda area: str(area.id), form["areas"]))
                        program_partner, _ = ProgramPartnerThrough.objects.update_or_create(
                            partner=form["partner"],
                            program=program,
                        )
                        program_partner.areas.set(areas_ids)
                    elif form and form["DELETE"]:
                        ProgramPartnerThrough.objects.filter(partner=form["partner"], program=program).delete()
                return HttpResponseRedirect(reverse("admin:program_program_partners", args=[pk]))

        context["program_area_formset"] = partner_area_form_set
        context["business_area"] = program.business_area
        context["areas"] = Area.objects.filter(area_type__country__business_areas__id=program.business_area.id)
        context["partners"] = Partner.objects.filter(
            Q(allowed_business_areas=program.business_area) | Q(name="UNICEF")
        ).order_by("name")
        context["program"] = program
        context["unicef_partner_id"] = Partner.objects.get(name="UNICEF").id

        if is_editable:
            return TemplateResponse(request, "admin/program/program/program_partner_access.html", context)
        else:
            return TemplateResponse(request, "admin/program/program/program_partner_access_readonly.html", context)
