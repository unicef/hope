from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from django import forms
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase, LastSyncDateResetMixin
from hope.models import BeneficiaryGroup, Program


class BeneficiaryGroupForm(forms.ModelForm):
    class Meta:
        model = BeneficiaryGroup
        fields = (
            "name",
            "group_label",
            "group_label_plural",
            "member_label",
            "member_label_plural",
            "payee_type",
            "data_collecting_types",
            "active",
        )

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        payee_type = cleaned_data.get("payee_type")
        data_collecting_types = cleaned_data.get("data_collecting_types")
        if payee_type and data_collecting_types and data_collecting_types.exclude(payee_type=payee_type).exists():
            self.add_error("data_collecting_types", "Data Collecting Types must belong to the selected Payee Type")
        if (
            not self.instance._state.adding
            and payee_type
            and payee_type.pk != self.instance.payee_type_id
            and Program.all_objects.filter(beneficiary_group=self.instance).exists()
        ):
            self.add_error("payee_type", "Cannot change the Payee Type of a Payee Label used by programs")
        return cleaned_data


@admin.register(BeneficiaryGroup)
class BeneficiaryGroupAdmin(LastSyncDateResetMixin, HOPEModelAdminBase):
    form = BeneficiaryGroupForm
    list_display = (
        "name",
        "payee_type",
        "active",
        "group_label",
        "group_label_plural",
        "member_label",
        "member_label_plural",
    )
    list_filter = (
        ("payee_type", AutoCompleteFilter),
        "active",
    )
    search_fields = (
        "name",
        "group_label",
        "group_label_plural",
        "member_label",
        "member_label_plural",
    )
    filter_horizontal = ("data_collecting_types",)
    ordering = ("name",)
