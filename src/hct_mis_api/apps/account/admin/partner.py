from typing import Any, Optional, Sequence, Type

from django import forms
from django.contrib import admin
from django.forms import CheckboxSelectMultiple, ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from adminfilters.autocomplete import AutoCompleteFilter

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.admin.user_role import RoleAssignmentInline
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.admin import HopeModelAdminMixin
from mptt.forms import TreeNodeMultipleChoiceField


def can_add_business_area_to_partner(request: Any, *args: Any, **kwargs: Any) -> bool:
    return request.user.can_add_business_area_to_partner()


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
    exclude = ("allowed_business_areas",)
    inlines = (RoleAssignmentInline,)

    def get_inline_instances(self, request: Any, obj: Optional[account_models.Partner] = None) -> list:
        if obj is None:  # if object is being created now, disable the inlines
            return []
        return super().get_inline_instances(request, obj)

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
