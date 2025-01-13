from collections import defaultdict
from typing import TYPE_CHECKING, Any, Optional, Sequence, Type, Union
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.forms import CheckboxSelectMultiple, ModelForm, formset_factory
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from admin_extra_buttons.decorators import button
from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.admin.user_role import RoleAssignmentInline
from hct_mis_api.apps.account.models import IncompatibleRoles, Role, RoleAssignment, Partner
from hct_mis_api.apps.core.models import BusinessArea, BusinessAreaPartnerThrough
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.admin import HopeModelAdminMixin
from mptt.forms import TreeNodeMultipleChoiceField

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


def can_add_business_area_to_partner(request: Any, *args: Any, **kwargs: Any) -> bool:
    return request.user.can_add_business_area_to_partner()


# TODO: perm - not needed but replace with LimitAreasForPartner
# def business_area_role_form_custom_query(queryset: "QuerySet") -> Any:
#     class BusinessAreaRoleForm(forms.Form):
#         business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all(), required=True)
#         program = forms.ModelChoiceField(queryset=Program.objects.all(), required=False)
#         role = forms.ModelChoiceField(queryset=Role.objects.filter(is_available_for_partner=True).all(), required=True)
#         expiry_date = forms.DateField(required=False)
#
#         def __init__(self, *args: Any, **kwargs: Any) -> None:
#             super().__init__(*args, **kwargs)
#             self.fields["business_area"].queryset = queryset
#
#     return BusinessAreaRoleForm


class ProgramAreaForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all(), required=True)
    program = forms.ModelChoiceField(queryset=Program.objects.all(), required=True)
    areas = TreeNodeMultipleChoiceField(queryset=Area.objects.all(), widget=CheckboxSelectMultiple(), required=False)


class PartnerAdminForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name', 'allowed_business_areas', 'is_un', 'parent']

    def clean_allowed_business_areas(self):
        # Get the original allowed business areas for the partner
        partner = self.instance
        previous_allowed_ba = set(partner.allowed_business_areas.all())

        # Get the allowed business from form submission
        current_allowed_ba = set(self.cleaned_data.get('allowed_business_areas'))

        # Identify which business areas were removed
        removed_ba = previous_allowed_ba - current_allowed_ba

        # Check if there are any removed business areas with existing role assignments
        for ba in removed_ba:
            if RoleAssignment.objects.filter(partner=partner, business_area=ba).exists():
                # Add a form error instead of raising a ValidationError
                self.add_error(
                    'allowed_business_areas',
                    f"You cannot remove {ba} because there are existing role assignments for this business area."
                )

        return self.cleaned_data.get('allowed_business_areas', [])


@admin.register(account_models.Partner)
class PartnerAdmin(HopeModelAdminMixin, admin.ModelAdmin):
    form = PartnerAdminForm
    list_filter = ("is_un", "parent")
    search_fields = ("name",)
    readonly_fields = ("sub_partners",)
    list_display = (
        "__str__",
        "sub_partners",
        "is_un",
    )
    filter_horizontal = ("allowed_business_areas",)
    inlines = (RoleAssignmentInline,)

    def sub_partners(self, obj: Any) -> Optional[str]:
        return self.links_to_objects(obj.get_children()) if obj else None

    sub_partners.short_description = "Sub-Partners"

    @classmethod
    def links_to_objects(cls, objects: Any) -> str:
        rel_list = "<ul>"
        for obj in objects:
            link = reverse("admin:account_partner_change", args=[obj.id])
            rel_list += "<li><a href='%s'>%s</a></li>" % (link, obj.name)
        rel_list += "</ul>"
        return format_html(rel_list)

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[account_models.Partner] = None) -> Sequence[str]:
        additional_fields = []
        if obj and obj.is_unicef:
            additional_fields.append("name")
        if not request.user.has_perm("account.can_change_allowed_business_areas"):
            additional_fields.append("allowed_business_areas")
        return list(super().get_readonly_fields(request, obj)) + additional_fields

    def get_form(
        self, request: HttpRequest, obj: Optional[account_models.Partner] = None, change: bool = False, **kwargs: Any
    ) -> Type[ModelForm]:
        form = super().get_form(request, obj, **kwargs)

        queryset = account_models.Partner.objects.filter(level=0)
        if obj:
            if obj.is_parent:
                queryset = account_models.Partner.objects.none()
            else:
                queryset = queryset.exclude(id=obj.id)

        form.base_fields["parent"].queryset = queryset
        return form

    # TODO: perm - not needed but replace with LimitAreasForPartner
    # @button(enabled=lambda obj: obj.original.is_editable)
    # def permissions(self, request: HttpRequest, pk: int) -> Union[TemplateResponse, HttpResponseRedirect]:
    #     context = self.get_common_context(request, pk, title="Partner permissions")
    #     partner: account_models.Partner = context["original"]
    #     user_can_add_ba_to_partner = request.user.can_add_business_area_to_partner()
    #     role_assignment_list = partner.role_assignments.all()
    #     context["can_add_business_area_to_partner"] = user_can_add_ba_to_partner
    #
    #     BusinessAreaRoleFormSet = formset_factory(
    #         business_area_role_form_custom_query(partner.allowed_business_areas.all()),
    #         extra=0,
    #         can_delete=True,
    #     )
    #     if request.method == "GET":
    #         business_area_role_data = []
    #         for role_assignment in role_assignment_list:
    #             print("dassad")
    #             print(role_assignment.__dict__)
    #             business_area_role_data.append(
    #                 {"business_area": role_assignment.business_area_id, "program": role_assignment.program.id if role_assignment.program else None, "role": role_assignment.role, "expiry_date": str(role_assignment.expiry_date)}
    #             )
    #         business_area_role_form_set = BusinessAreaRoleFormSet(
    #             initial=business_area_role_data, prefix="business_area_role"
    #         )
    #     else:
    #         business_area_role_form_set = BusinessAreaRoleFormSet(request.POST or None, prefix="business_area_role")
    #         role_assignment_data_be_deleted = []
    #
    #         business_area_role_form_set_is_valid = business_area_role_form_set.is_valid()
    #         if user_can_add_ba_to_partner and business_area_role_form_set_is_valid:
    #             for form in business_area_role_form_set.cleaned_data:
    #                 if form and not form["DELETE"]:
    #                     business_area_id = str(form["business_area"].id)
    #                     program_id = str(form["program"].id) if form["program"] else None
    #                     role_id = str(form["role"].id)
    #
    #                     RoleAssignment.objects.get_or_create(
    #                         partner=partner,
    #                         business_area_id=business_area_id,
    #                         program_id=program_id,
    #                         role_id=role_id,
    #                     )
    #                 elif form["DELETE"]:
    #                     role_assignment_data_be_deleted.append(
    #                         RoleAssignment.objects.filter(
    #                             partner=partner, business_area=form["business_area"], program=form["program"], role=form["role"]
    #                         )
    #                         .first()
    #                         .id
    #                     )
    #
    #         if business_area_role_form_set_is_valid:
    #             if role_assignment_data_be_deleted:
    #                 RoleAssignment.objects.filter(pk__in=role_assignment_data_be_deleted).delete()
    #
    #             return HttpResponseRedirect(reverse("admin:account_partner_change", args=[pk]))
    #
    #     context["business_area_role_formset"] = business_area_role_form_set
    #
    #     return TemplateResponse(request, "admin/account/parent/permissions.html", context)
