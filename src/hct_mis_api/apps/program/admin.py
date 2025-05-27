from typing import Any, Optional, Union

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin
from django import forms
from django.contrib import admin, messages
from django.db.models import Q, QuerySet
from django.forms import CheckboxSelectMultiple, formset_factory
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from mptt.forms import TreeNodeMultipleChoiceField

from hct_mis_api.apps.account.models import AdminAreaLimitedTo, Partner
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.documents import (HouseholdDocument,
                                                  get_individual_doc)
from hct_mis_api.apps.household.forms import CreateTargetPopulationTextForm
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import (BeneficiaryGroup, Program,
                                             ProgramCycle)
from hct_mis_api.apps.registration_datahub.services.biometric_deduplication import \
    BiometricDeduplicationService
from hct_mis_api.apps.targeting.celery_tasks import create_tp_from_list
from hct_mis_api.apps.targeting.models import TargetingCriteria
from hct_mis_api.apps.utils.admin import (HOPEModelAdminBase,
                                          LastSyncDateResetMixin,
                                          SoftDeletableAdminMixin)
from hct_mis_api.apps.utils.elasticsearch_utils import populate_index


@admin.register(ProgramCycle)
class ProgramCycleAdmin(LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("title", "program", "status", "start_date", "end_date", "created_by")
    date_hierarchy = "start_date"
    list_filter = (
        ("program__business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("created_by", AutoCompleteFilter),
        ("status", ChoicesFieldComboFilter),
    )
    search_fields = ("title", "program__name")
    raw_id_fields = ("program", "created_by")
    exclude = ("unicef_id",)


class ProgramCycleAdminInline(admin.TabularInline):
    model = ProgramCycle
    extra = 0
    fields = readonly_fields = (
        "unicef_id",
        "title",
        "status",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
        "created_by",
    )
    ordering = ["-start_date"]
    raw_id_fields = ("created_by",)


class PartnerAreaLimitForm(forms.Form):
    partner = forms.ModelChoiceField(queryset=Partner.objects.all(), required=True)
    areas = TreeNodeMultipleChoiceField(
        queryset=Area.objects.filter(area_type__area_level__lte=3), widget=CheckboxSelectMultiple(), required=True
    )


@admin.register(Program)
class ProgramAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, AdminAutoCompleteSearchMixin, HOPEModelAdminBase):
    list_display = (
        "name",
        "programme_code",
        "status",
        "start_date",
        "end_date",
        "business_area",
        "data_collecting_type",
        "beneficiary_group",
        "sector",
        "scope",
        "frequency_of_payments",
        "partner_access",
        "biometric_deduplication_enabled",
        "cash_plus",
        "is_visible",
    )
    date_hierarchy = "start_date"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("data_collecting_type", AutoCompleteFilter),
        ("beneficiary_group", AutoCompleteFilter),
        ("scope", ChoicesFieldComboFilter),
        ("sector", ChoicesFieldComboFilter),
        "frequency_of_payments",
        ("partner_access", ChoicesFieldComboFilter),
        "biometric_deduplication_enabled",
        "cash_plus",
        "is_visible",
    )
    search_fields = ("name", "programme_code")
    raw_id_fields = ("business_area", "data_collecting_type", "beneficiary_group", "admin_areas")
    filter_horizontal = ("admin_areas", "partners")

    inlines = (ProgramCycleAdminInline,)
    ordering = ("name",)

    def save_model(self, request: HttpRequest, obj: Program, *args: Any) -> None:
        if obj.pk:
            original = Program.objects.get(pk=obj.pk)
            if original.biometric_deduplication_enabled != obj.biometric_deduplication_enabled:
                service = BiometricDeduplicationService()
                if obj.biometric_deduplication_enabled:
                    service.mark_rdis_as_pending(obj)
                else:
                    service.delete_deduplication_set(obj)
        super().save_model(request, obj, *args)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Program]:
        return (
            super().get_queryset(request).select_related("data_collecting_type", "business_area", "beneficiary_group")
        )

    @button(
        permission="payment.add_paymentplan",
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
            create_tp_from_list.delay(request.POST.dict(), str(request.user.pk), str(program.pk))
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

    @button(permission="account.can_change_area_limits")
    def area_limits(self, request: HttpRequest, pk: int) -> Union[TemplateResponse, HttpResponseRedirect]:
        context = self.get_common_context(request, pk, title="Admin Area Limits")
        program: Program = context["original"]
        PartnerAreaLimitFormSet = formset_factory(PartnerAreaLimitForm, extra=0, can_delete=True)

        is_editable = program.partner_access == Program.SELECTED_PARTNERS_ACCESS

        if request.method == "GET" or not is_editable:
            partner_area_data = []
            for area_limits in program.admin_area_limits.all():
                partner_area_data.append(
                    {
                        "partner": area_limits.partner,
                        "areas": [str(area_id) for area_id in area_limits.areas.values_list("id", flat=True)],
                    }
                )
            partner_area_form_set = PartnerAreaLimitFormSet(initial=partner_area_data, prefix="program_areas")
        elif request.method == "POST":
            partner_area_form_set = PartnerAreaLimitFormSet(request.POST or None, prefix="program_areas")
            if partner_area_form_set.is_valid():
                for partner_area_form in partner_area_form_set:
                    form = partner_area_form.cleaned_data
                    if form and not form["DELETE"]:
                        areas_ids = list(map(lambda area: str(area.id), form["areas"]))
                        program_partner, _ = AdminAreaLimitedTo.objects.update_or_create(
                            partner=form["partner"],
                            program=program,
                        )
                        program_partner.areas.set(areas_ids)
                    elif form and form["DELETE"]:
                        AdminAreaLimitedTo.objects.filter(partner=form["partner"], program=program).delete()
                return HttpResponseRedirect(reverse("admin:program_program_area_limits", args=[pk]))

        context["program_area_formset"] = partner_area_form_set
        context["business_area"] = program.business_area
        context["areas"] = Area.objects.filter(area_type__country__business_areas__id=program.business_area.id)
        # it's only possible to create area limits for partners that have a role in this program
        context["partners"] = (
            Partner.objects.filter(
                Q(role_assignments__program=program)
                | (Q(role_assignments__business_area=program.business_area) & Q(role_assignments__program__isnull=True))
            )
            .exclude(parent__name="UNICEF")
            .order_by("name")
        )
        context["program"] = program

        if is_editable:
            return TemplateResponse(request, "admin/program/program/program_area_limits.html", context)
        else:
            return TemplateResponse(request, "admin/program/program/program_area_limits_readonly.html", context)

    @button(permission="account.can_reindex_programs")
    def reindex_program(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:
        program = Program.objects.get(pk=pk)
        populate_index(
            Individual.all_merge_status_objects.filter(program=program),
            get_individual_doc(program.business_area.slug),
        )
        populate_index(Household.all_merge_status_objects.filter(program=program), HouseholdDocument)
        messages.success(request, f"Program {program.name} reindexed.")
        return HttpResponseRedirect(reverse("admin:program_program_changelist"))


@admin.register(BeneficiaryGroup)
class BeneficiaryGroupAdmin(LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("name", "group_label", "group_label_plural", "member_label", "member_label_plural", "master_detail")
    search_fields = (
        "name",
        "group_label",
        "group_label_plural",
        "member_label",
        "member_label_plural",
    )
    ordering = ("name",)
