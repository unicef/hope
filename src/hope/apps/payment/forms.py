from typing import Any

from django import forms
from django.contrib.postgres.forms import DecimalRangeField

from hope.apps.payment.models import (
    AcceptanceProcessThreshold,
    FinancialServiceProviderXlsxTemplate,
)


class AcceptanceProcessThresholdForm(forms.ModelForm):
    payments_range_usd = DecimalRangeField(
        fields=[
            forms.IntegerField(required=True),
            forms.IntegerField(required=False),
        ],
    )

    class Meta:
        model = AcceptanceProcessThreshold
        fields = [
            "payments_range_usd",
            "approval_number_required",
            "authorization_number_required",
            "finance_release_number_required",
        ]


class TemplateSelectForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=FinancialServiceProviderXlsxTemplate.objects.none(), label="Select FSP XLSX Template", required=False
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        payment_plan = kwargs.pop("payment_plan")
        super().__init__(*args, **kwargs)
        self.fields["template"].queryset = FinancialServiceProviderXlsxTemplate.objects.filter(
            financial_service_providers__allowed_business_areas__slug=payment_plan.business_area.slug
        ).distinct()
