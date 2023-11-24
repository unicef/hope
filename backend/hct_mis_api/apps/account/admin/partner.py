from typing import Union

from django import forms
from django.contrib import admin
from django.forms import CheckboxSelectMultiple, formset_factory
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_buttons.decorators import button

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.models import PartnerPermission, Role
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.admin import HopeModelAdminMixin
from mptt.forms import TreeNodeMultipleChoiceField


class BusinessAreaRoleForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all(), required=True)
    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.all(), required=True)


class ProgramAreaForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all(), required=True)
    program = forms.ModelChoiceField(queryset=Program.objects.all(), required=True)
    areas = TreeNodeMultipleChoiceField(queryset=Area.objects.all(), widget=CheckboxSelectMultiple(), required=False)


@admin.register(account_models.Partner)
class PartnerAdmin(HopeModelAdminMixin, admin.ModelAdmin):
    list_filter = ("is_un",)
    search_fields = ("name",)
    readonly_fields = ("permissions",)
    list_display = (
        "name",
        "is_un",
    )

    @button()
    def permissions(self, request: HttpRequest, pk: int) -> Union[TemplateResponse, HttpResponseRedirect]:
        context = self.get_common_context(request, pk, title="Partner permissions")
        parent: account_models.Partner = context["original"]

        BusinessAreaRoleFormSet = formset_factory(BusinessAreaRoleForm, extra=0, can_delete=True)
        ProgramAreaFormSet = formset_factory(ProgramAreaForm, extra=0, can_delete=True)

        business_areas = set()

        if request.method == "GET":
            permissions_list = parent.get_permissions().to_list()
            business_area_role_data = []
            program_area_data = []
            for permission in permissions_list:
                if permission.roles:
                    business_area_role_data.append(
                        {"business_area": permission.business_area_id, "roles": permission.roles}
                    )
            for permission in permissions_list:
                for program_id, areas in permission.programs.items():
                    program_area_data.append(
                        {"business_area": permission.business_area_id, "program": program_id, "areas": areas}
                    )
                    business_areas.add(permission.business_area_id)
            business_area_role_form_set = BusinessAreaRoleFormSet(
                initial=business_area_role_data, prefix="business_area_role"
            )
            program_area_form_set = ProgramAreaFormSet(initial=program_area_data, prefix="program_areas")
        else:
            partner_permissions = PartnerPermission()
            business_area_role_form_set = BusinessAreaRoleFormSet(request.POST or None, prefix="business_area_role")
            program_area_form_set = ProgramAreaFormSet(request.POST or None, prefix="program_areas")
            refresh_areas = request.POST["refresh-areas"]

            if business_area_role_form_set.is_valid():
                for form in business_area_role_form_set.cleaned_data:
                    if form:
                        business_area_id = str(form["business_area"].id)
                        role_ids = list(map(lambda role: str(role.id), form["roles"]))
                        if not form["DELETE"]:
                            partner_permissions.set_roles(business_area_id, role_ids)

            if program_area_form_set.is_valid():
                for form in program_area_form_set.cleaned_data:
                    if form:
                        business_area_id = str(form["business_area"].id)
                        program_id = str(form["program"].id)
                        areas_ids = list(map(lambda area: str(area.id), form["areas"]))
                        if not form["DELETE"]:
                            partner_permissions.set_program_areas(business_area_id, program_id, areas_ids)

            for program_area_form in program_area_form_set:
                if program_area_form.cleaned_data.get("business_area"):
                    business_areas.add(program_area_form.cleaned_data["business_area"].id)

            if refresh_areas == "false" and business_area_role_form_set.is_valid() and program_area_form_set.is_valid():
                parent.set_permissions(partner_permissions)
                parent.save()

                return HttpResponseRedirect(reverse("admin:account_partner_change", args=[pk]))

        context["business_area_role_formset"] = business_area_role_form_set
        context["program_area_formset"] = program_area_form_set
        context["areas"] = {}

        for business_area_id in business_areas:
            context["areas"][str(business_area_id)] = Area.objects.filter(
                area_type__country__business_areas__id=business_area_id
            )

        return TemplateResponse(request, "admin/account/parent/permissions.html", context)
