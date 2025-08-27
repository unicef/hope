from typing import Any, Sequence

from adminfilters.autocomplete import AutoCompleteFilter
from django import forms
from django.contrib import admin
from django.forms import CheckboxSelectMultiple, ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from mptt.forms import TreeNodeMultipleChoiceField

from hope.models.partner import Partner
from hope.admin.user_role import RoleAssignmentInline
from hope.admin.utils import HopeModelAdminMixin
from hope.models.business_area import BusinessArea
from hope.models.area import Area
from hope.models.program import Program


def can_add_business_area_to_partner(request: Any, *args: Any, **kwargs: Any) -> bool:
    return request.user.can_add_business_area_to_partner()


class ProgramAreaForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all(), required=True)
    program = forms.ModelChoiceField(queryset=Program.objects.all(), required=True)
    areas = TreeNodeMultipleChoiceField(queryset=Area.objects.all(), widget=CheckboxSelectMultiple(), required=False)


@admin.register(Partner)
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

    def get_inline_instances(self, request: Any, obj: Partner | None = None) -> list:
        if obj is None:  # if object is being created now, disable the inlines
            return []
        return super().get_inline_instances(request, obj)

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

    def get_readonly_fields(self, request: HttpRequest, obj: Partner | None = None) -> Sequence[str]:
        additional_fields = []
        if obj and (obj.is_unicef or obj.is_unicef_subpartner):
            additional_fields.extend(["name", "parent"])
        return list(super().get_readonly_fields(request, obj)) + additional_fields

    def get_form(
        self, request: HttpRequest, obj: Partner | None = None, change: bool = False, **kwargs: Any
    ) -> type[ModelForm]:
        form = super().get_form(request, obj, **kwargs)

        if not (obj and (obj.is_unicef_subpartner or obj.is_unicef)):
            queryset = Partner.objects.filter(level=0)
            if obj:
                if obj.is_parent:
                    queryset = Partner.objects.none()
                else:
                    queryset = queryset.exclude(id=obj.id)

            form.base_fields["parent"].queryset = queryset
        return form
