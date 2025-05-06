from collections import defaultdict
from typing import TYPE_CHECKING, Any, Sequence

from django import forms
from django.contrib import admin, messages
from django.forms import CheckboxSelectMultiple, ModelForm, formset_factory
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.models import IncompatibleRoles, Role
from hct_mis_api.apps.core.models import BusinessArea, BusinessAreaPartnerThrough
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.admin import HopeModelAdminMixin
from mptt.forms import TreeNodeMultipleChoiceField

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


def can_add_business_area_to_partner(request: Any, *args: Any, **kwargs: Any) -> bool:
    return request.user.can_add_business_area_to_partner()


def business_area_role_form_custom_query(queryset: "QuerySet") -> Any:
    class BusinessAreaRoleForm(forms.Form):
        business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all(), required=True)
        roles = forms.ModelMultipleChoiceField(queryset=Role.objects.all(), required=True)

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.fields["business_area"].queryset = queryset

    return BusinessAreaRoleForm


class ProgramAreaForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all(), required=True)
    program = forms.ModelChoiceField(queryset=Program.objects.all(), required=True)
    areas = TreeNodeMultipleChoiceField(queryset=Area.objects.all(), widget=CheckboxSelectMultiple(), required=False)


@admin.register(account_models.Partner)
class PartnerAdmin(HopeModelAdminMixin, admin.ModelAdmin):
    list_filter = ("is_un", ("parent", AutoCompleteFilter))
    search_fields = ("name",)
    readonly_fields = ("sub_partners",)
    list_display = (
        "name",
        "parent",
        "sub_partners",
        "is_un",
    )
    filter_horizontal = ("allowed_business_areas",)

    def sub_partners(self, obj: Any) -> str | None:
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

    def get_readonly_fields(self, request: HttpRequest, obj: account_models.Partner | None = None) -> Sequence[str]:
        additional_fields = []
        if obj and obj.is_unicef:
            additional_fields.append("name")
        if not request.user.has_perm("account.can_change_allowed_business_areas"):
            additional_fields.append("allowed_business_areas")
        return list(super().get_readonly_fields(request, obj)) + additional_fields

    def get_form(
        self, request: HttpRequest, obj: account_models.Partner | None = None, change: bool = False, **kwargs: Any
    ) -> type[ModelForm]:
        form = super().get_form(request, obj, **kwargs)

        queryset = account_models.Partner.objects.filter(level=0)
        if obj:
            if obj.is_parent:
                queryset = account_models.Partner.objects.none()
            else:
                queryset = queryset.exclude(id=obj.id)

        form.base_fields["parent"].queryset = queryset
        return form

    @button(enabled=lambda obj: obj.original.is_editable, permission="auth.view_permission")
    def permissions(self, request: HttpRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
        context = self.get_common_context(request, pk, title="Partner permissions")
        partner: account_models.Partner = context["original"]
        user_can_add_ba_to_partner = request.user.can_add_business_area_to_partner()
        permissions_list = partner.business_area_partner_through.all()
        context["can_add_business_area_to_partner"] = user_can_add_ba_to_partner

        BusinessAreaRoleFormSet = formset_factory(
            business_area_role_form_custom_query(partner.allowed_business_areas.all()),
            extra=0,
            can_delete=True,
        )
        if request.method == "GET":
            business_area_role_data = []
            for permission in permissions_list:
                if permission.roles:
                    business_area_role_data.append(
                        {"business_area": permission.business_area_id, "roles": permission.roles.all()}
                    )
            business_area_role_form_set = BusinessAreaRoleFormSet(
                initial=business_area_role_data, prefix="business_area_role"
            )
        else:
            business_area_role_form_set = BusinessAreaRoleFormSet(request.POST or None, prefix="business_area_role")
            incompatible_roles = defaultdict(list)
            ba_partner_through_data = {}
            ba_partner_through_to_be_deleted = []

            business_area_role_form_set_is_valid = business_area_role_form_set.is_valid()
            if user_can_add_ba_to_partner and business_area_role_form_set_is_valid:
                for form in business_area_role_form_set.cleaned_data:
                    if form and not form["DELETE"]:
                        business_area_id = str(form["business_area"].id)
                        role_ids = [str(role.id) for role in form["roles"]]

                        if incompatible_role := IncompatibleRoles.objects.filter(
                            role_one__in=role_ids, role_two__in=role_ids
                        ).first():
                            incompatible_roles[form["business_area"]].append(str(incompatible_role))
                        else:
                            ba_partner, _ = BusinessAreaPartnerThrough.objects.get_or_create(
                                partner=partner,
                                business_area_id=business_area_id,
                            )
                            ba_partner_through_data[ba_partner] = form["roles"]
                    elif form["DELETE"]:
                        ba_partner_through_to_be_deleted.append(
                            BusinessAreaPartnerThrough.objects.filter(
                                partner=partner, business_area=form["business_area"]
                            )
                            .first()
                            .id
                        )

            if incompatible_roles:
                for business_area, roles in incompatible_roles.items():
                    self.message_user(
                        request, f"Roles in {business_area} are incompatible: {', '.join(roles)}", messages.ERROR
                    )

            if business_area_role_form_set_is_valid and not incompatible_roles:
                if ba_partner_through_to_be_deleted:
                    BusinessAreaPartnerThrough.objects.filter(pk__in=ba_partner_through_to_be_deleted).delete()
                for ba_partner_through, areas in ba_partner_through_data.items():
                    ba_partner_through.roles.add(*areas)

                return HttpResponseRedirect(reverse("admin:account_partner_change", args=[pk]))

        context["business_area_role_formset"] = business_area_role_form_set

        return TemplateResponse(request, "admin/account/parent/permissions.html", context)
