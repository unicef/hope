from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib.postgres.forms import DecimalRangeField

from hope.models import AcceptanceProcessThreshold, FinancialServiceProviderXlsxTemplate

if TYPE_CHECKING:
    from hope.models import PaymentPlanGroup


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


class BatchReexportForm(forms.Form):
    export_tag = forms.ChoiceField(choices=[], label="Batch to re-export")
    template = forms.ModelChoiceField(
        queryset=FinancialServiceProviderXlsxTemplate.objects.all(),
        required=False,
        label="FSP XLSX Template (optional override)",
    )

    def __init__(self, *args: Any, payment_plan_group: "PaymentPlanGroup | None" = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if payment_plan_group is not None:
            tags = (
                payment_plan_group.payment_plans.filter(export_tag__isnull=False)
                .values_list("export_tag", flat=True)
                .distinct()
                .order_by("export_tag")
            )
            self.fields["export_tag"].choices = [(t, f"Batch {t}") for t in tags]
