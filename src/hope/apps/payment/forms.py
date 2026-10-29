from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib.postgres.forms import DecimalRangeField

from hope.contrib.vision.models import FundsCommitmentHeader
from hope.models import AcceptanceProcessThreshold, FinancialServiceProviderXlsxTemplate

if TYPE_CHECKING:
    from hope.models import PaymentPlanGroup


class VisionFundsCommitmentHeaderAssignmentForm(forms.Form):
    funds_commitment_headers = forms.ModelMultipleChoiceField(
        queryset=FundsCommitmentHeader.objects.none(),
        label="Funds Commitment Headers",
    )

    def __init__(self, *args: Any, payment_plan_group: "PaymentPlanGroup", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        headers = (
            FundsCommitmentHeader.objects.filter(funds_commitment_items__office=payment_plan_group.business_area)
            .distinct()
            .order_by("funds_commitment_number")
        )
        self.fields["funds_commitment_headers"].queryset = headers


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


class GroupReexportForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=FinancialServiceProviderXlsxTemplate.objects.all(),
        required=False,
        label="FSP XLSX Template (optional override)",
    )
